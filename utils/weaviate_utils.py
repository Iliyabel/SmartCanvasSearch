import weaviate
import weaviate.classes.config as wvcc
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import Filter
import weaviate.classes.query as wq
from weaviate.util import generate_uuid5
import json
import os
from .general_utils import extractTextFromPdf, extractTextFromPPTX, extractTextFromDocx, extractTextFromTxt, semantic_chunking, encode_text
import nltk

def print_header(msg): print(f"\n--- {msg} ---")
def print_status(msg): print(f"[STATUS] {msg}")
def print_warning(msg, detail=""): print(f"[WARNING] {msg} {detail}")

try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    print_status("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt')
    
# Determine project root from weaviate_utils.py's location for standalone use
WEAVIATE_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_FROM_WEAVIATE_UTILS = os.path.dirname(WEAVIATE_UTILS_DIR)


# Initialize and return a weaviate client.
def create_client(url="http://localhost:8080", grpc_port=50051):
    try:
        client = weaviate.connect_to_local(
            host="localhost", # Docker exposes on localhost
            port=8080,        # Default HTTP port from docker-compose
            grpc_port=grpc_port # Default gRPC port
        )

        if client.is_ready(): 
            print_status(f"Successfully connected to Weaviate at {url}")
            return client
        else:
            raise Exception("Weaviate is not ready after connection attempt.")
    except Exception as e:
        print_warning(f"Weaviate connection error to {url} (gRPC port {grpc_port}):", str(e))
        return None


# Creates the weaviate schema
def create_schema(client):
    """
    Creates the schema for Weaviate database.
    The schema consists of three collections: Course, File, and Chunk.
    Each collection has its own properties and vectorizer configuration.

    Args:
        client (weaviate.Client): The Weaviate client instance.

    Returns:
        None

    Raises:
        Exception: If the schema creation fails.

    This function creates the schema for the Weaviate database, including collections for courses, files, and chunks.
    It checks if the schema already exists before attempting to create it. If the schema is created successfully,
    it prints a success message. If the schema already exists, it skips the creation process.
    The schema includes the following collections:
        - Course: Contains metadata about courses.
        - File: Contains metadata about files associated with courses.
        - Chunk: Contains text chunks extracted from files for vector search.
    """
    schema = client.collections
    
    # Check if schema is already created
    if schema.exists("Course") and schema.exists("File") and schema.exists("Chunk"):
        print_status("Schema (Course, File, Chunk collections) already exists. Skipping creation.")
        return
    
    # Add Course collection to schema
    if not schema.exists("Course"):
        schema.create(
            name="Course",
            properties=[
                Property(name="name", data_type=DataType.TEXT),
                Property(name="course_id", data_type=DataType.INT),
                Property(name="course_code", data_type=DataType.TEXT),
                Property(name="start_date", data_type=DataType.DATE, skip_vectorization=True),
                Property(name="end_date", data_type=DataType.DATE, skip_vectorization=True),
                Property(name="uuid", data_type=DataType.TEXT, skip_vectorization=True),
                
            ],
            description="A Canvas course with relevant metadata",
            vectorizer_config=wvcc.Configure.Vectorizer.none(),
        )
        print_status("Created 'Course' collection.")


    # Add File collection to schema
    if not schema.exists("File"):
        schema.create(
            name="File",
            properties=[
                Property(name="file_id", data_type=DataType.INT),
                Property(name="uuid", data_type=DataType.TEXT, skip_vectorization=True),
                Property(name="display_name", data_type=DataType.TEXT, skip_vectorization=True),
                Property(name="file_type", data_type=DataType.TEXT, skip_vectorization=True),
                Property(name="local_file_path", data_type=DataType.TEXT, skip_vectorization=True),
                Property(name="url", data_type=DataType.TEXT, skip_vectorization=True),
                Property(name="size_bytes", data_type=DataType.INT, skip_vectorization=True),
                Property(name="created_at", data_type=DataType.DATE, skip_vectorization=True),
                Property(name="modified_at", data_type=DataType.DATE, skip_vectorization=True),
                Property(name="filename", data_type=DataType.TEXT, skip_vectorization=True),
                Property(name="course_id", data_type=DataType.INT, skip_vectorization=True),
            ],
            description="A file belonging to a course",
            vectorizer_config=wvcc.Configure.Vectorizer.none(),
        )
        print_status("Created 'File' collection.")
    

    # Add Chunk collection to schema
    if not schema.exists("Chunk"):
        schema.create(
            name="Chunk",
            properties=[
                Property(name="chunk_text", data_type=DataType.TEXT),
                Property(name="chunk_index", data_type=DataType.INT, skip_vectorization=True), # Overall index within the file
                Property(name="file_id", data_type=DataType.INT, skip_vectorization=True),
                Property(name="course_id", data_type=DataType.INT, skip_vectorization=True),
                Property(name="file_name", data_type=DataType.TEXT, skip_vectorization=True),
                Property(name="source_location", data_type=DataType.TEXT, skip_vectorization=True),
            ],
            description="A chunk of text from a file used for vector search",
            vectorizer_config=wvcc.Configure.Vectorizer.none(),
        )
        print_status("Created 'Chunk' collection.")

    print_status("Schema created successfully!")


# Deletes schema. For debugging.
def delete_schema(client):
    """
    Deletes the schema for Weaviate database.

    Args:
        client (weaviate.Client): The Weaviate client instance.

    Returns:
        None
    """
    client.collections.delete_all()
    print_status("Schema deleted.")


def prepare_courses_for_weaviate(json_file_path: str):
    """
    Extracts course data from a JSON file and prepares it for insertion into a Weaviate database.

    Args:
        json_file_path (str): Path to the JSON file containing course data.

    Returns:
        list: A list of dictionaries containing extracted course data.
    """
    try:
        # Load the JSON data
        with open(json_file_path, 'r', encoding='utf-8') as file:
            courses_raw = json.load(file)
        print_status(f"Loaded {len(courses_raw)} raw course entries from {json_file_path}")

        # Extract relevant fields
        prepared_data = []
        for course in courses_raw:
            if isinstance(course, dict) and all(key in course for key in ["name", "id", "course_code", "uuid"]):
                # Handle potentially null dates
                start_at = course.get("start_at")
                end_at = course.get("end_at")

                prepared_data.append({
                    "name": course["name"],
                    "course_id": course["id"], # This is the Canvas course ID
                    "course_code": course["course_code"],
                    "start_date": start_at,
                    "end_date": end_at,
                    "uuid": course["uuid"] # This is Canvas's UUID for the course
                })
        
        print_status(f"Prepared {len(prepared_data)} courses for Weaviate.")
        return prepared_data
    
    except FileNotFoundError:
        print_warning(f"Course list file not found at {json_file_path}")
        return []
    except json.JSONDecodeError:
        print_warning(f"Failed to decode JSON from {json_file_path}")
        return []
    except Exception as e:
        print_warning(f"An unexpected error occurred in prepare_courses_for_weaviate: {e}")
        return []
    

def prepare_files_for_weaviate(files_json_path: str, course_id: int, project_root: str):
    """
    Extracts file data from a JSON file (files.json for a course) and prepares it for Weaviate.
    Does NOT download files here. Assumes files are already downloaded.

    Args:
        json_file_path (str): Path to the JSON file containing file data.
        course_id (int): ID of the course to which the files belong.    
        
    Returns:
        list: A list of dictionaries containing extracted file data.
    """
    try:
        # Load the JSON data
        with open(files_json_path, 'r', encoding='utf-8') as file:
            files_raw = json.load(file)

        if not isinstance(files_raw, list): # Handle if files.json contains an error object
            print_warning(f"Expected a list in {files_json_path}, but found {type(files_raw)}. Content: {files_raw}")
            return []

        # Extract relevant fields
        prepared_data = []
        for file_info in files_raw:
            if isinstance(file_info, dict) and all(key in file_info for key in ["id", "uuid", "display_name", "mime_class", "url", "size", "created_at", "modified_at", "filename"]):
                local_file_path = os.path.join(project_root, "Courses", str(course_id), file_info["filename"])
                
                # Check if the local file actually exists
                if not os.path.exists(local_file_path):
                    print_warning(f"File {file_info['filename']} not found locally at {local_file_path}. Skipping Weaviate prep for this file.")
                    continue

                prepared_data.append({
                    "file_id": file_info["id"], # Canvas file ID
                    "canvas_file_uuid": file_info["uuid"], # Canvas's own UUID for the file
                    "display_name": file_info["display_name"],
                    "file_type": file_info.get("mime_class", "unknown"), # e.g., pdf, pptx (Canvas uses 'pdf', 'pptx' etc.)
                    "local_file_path": local_file_path, # Actual path
                    "url": file_info["url"], # Original download URL
                    "size_bytes": file_info["size"],
                    "created_at": file_info["created_at"],
                    "modified_at": file_info["modified_at"],
                    "filename": file_info["filename"],
                    "course_id": course_id # Canvas course ID
                })
        print_status(f"Prepared {len(prepared_data)} files for Weaviate from course {course_id}.")
        return prepared_data

    except FileNotFoundError:
        print_warning(f"Files JSON not found at {files_json_path}")
        return []
    except json.JSONDecodeError:
        print_warning(f"Failed to decode JSON from {files_json_path}")
        return []
    except Exception as e:
        print_warning(f"An unexpected error occurred in prepare_files_for_weaviate: {e}")
        return []


def prepare_chunks_for_weaviate(chunks: list[str]):
    """
    Prepares chunk data for insertion into a Weaviate database.

    Args:
        chunks (list[str]): List of chunk strings.

    Returns:
        list: A list of dictionaries containing prepared chunk data.
    """
    prepared = []
    for idx, chunk in enumerate(chunks):
        prepared.append({
            "chunk_text": chunk,
            "chunk_index": idx
        })
    return prepared


def insert_courses_into_weaviate(client, courses_prepared_data: list):
    """
    Reads course data from a JSON file, prepares it, and inserts it into the Weaviate database.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        json_file_path (str): Path to the JSON file containing course data.
    """
    if not courses_prepared_data:
        print_status("No prepared course data to insert.")
        return

    # Get the Course collection
    courses_collection = client.collections.get("Course")

    # Go through each course and add it to the collection
    with courses_collection.batch.dynamic() as batch:
        for course_props in courses_prepared_data:
            # Generate a Weaviate-specific UUID based on Canvas course_id to ensure idempotency
            weaviate_uuid = generate_uuid5(str(course_props["course_id"]), "Course")
            batch.add_object(
                properties=course_props,
                uuid=weaviate_uuid
            )

        # Check for failed objects
    if len(courses_collection.batch.failed_objects) > 0:
        print_warning(f"Failed to import {len(courses_collection.batch.failed_objects)} course objects.")
    else:
        print_status(f"Successfully inserted/updated {len(courses_prepared_data)} course objects.")


def check_if_chunks_exist_for_file(client, file_id: int, course_id: int) -> bool:
    """
    Checks if chunks for a given file_id and course_id already exist in Weaviate.
    """
    try:
        chunks_collection = client.collections.get("Chunk")
        response = chunks_collection.query.fetch_objects(
            filters=Filter.all_of([
                Filter.by_property("file_id").equal(file_id),
                Filter.by_property("course_id").equal(course_id)
            ]),
            limit=1
        )
        return len(response.objects) > 0
    except Exception as e:
        print_warning(f"Error checking for existing chunks for file_id {file_id}, course_id {course_id}: {e}")
        return False 


def insert_files_into_weaviate(client, files_prepared_data: list, course_id: int):
    """
    Reads file data from a JSON file, prepares it, and inserts it into the Weaviate database.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        json_file_path (str): Path to the JSON file containing file data.
        course_id (int): ID of the course to which the files belong.
    """
    if not files_prepared_data:
        print_status(f"No prepared file data to insert for course {course_id}.")
        return

    # Get the File collection
    files_collection = client.collections.get("File")
    
    # Collect all chunks from all files first, then batch insert them
    all_chunks_to_insert_with_vectors = []

    # Go through each file and add it to the collection
    with files_collection.batch.dynamic() as file_batch:
        for file_props in files_prepared_data:
            # Check if the file type is supported
            file_extension = file_props.get("filename", "").split('.')[-1].lower()
            supported_for_chunking = file_extension in ["pdf", "pptx", "docx", "txt"]
            canvas_file_id = file_props["file_id"] # Get the Canvas file ID

            if not supported_for_chunking:
                print_status(f"File type '{file_extension}' for '{file_props['filename']}' is not supported for text chunking. Inserting metadata only.")

            # Generate a Weaviate-specific UUID for the file object
            weaviate_file_uuid = generate_uuid5(str(canvas_file_id), "File")
            
            file_batch.add_object(
                properties=file_props, 
                uuid=weaviate_file_uuid
            )

            if supported_for_chunking:
                if check_if_chunks_exist_for_file(client, canvas_file_id, course_id):
                    print_status(f"SKIPPING chunking: Chunks for file '{file_props['filename']}' (ID: {canvas_file_id}) already exist in Weaviate.")
                    continue
                
                print_status(f"Processing file for chunking: {file_props['local_file_path']}")
                
                # Extract text and create chunks
                text_segments_with_locations: list[tuple[str, str]] = []
                try:
                    if file_extension == 'pdf':
                        text_segments_with_locations = extractTextFromPdf(file_props["local_file_path"])
                    elif file_extension == 'pptx':
                        text_segments_with_locations = extractTextFromPPTX(file_props["local_file_path"])
                    elif file_extension == 'docx':
                        text_segments_with_locations = extractTextFromDocx(file_props["local_file_path"])
                    elif file_extension == 'txt':
                        text_segments_with_locations = extractTextFromTxt(file_props["local_file_path"])
                except Exception as e:
                    print_warning(f"Failed to extract text segments from {file_props['local_file_path']}: {e}")
                    continue

                if not text_segments_with_locations:
                    print_status(f"No text segments extracted from {file_props['filename']}. Skipping chunk insertion.")
                    continue
                
                current_file_chunk_idx = 0 
                for text_segment, location_str in text_segments_with_locations:
                    if not text_segment.strip():
                        continue

                    # Chunk the current text_segment
                    segment_chunks_text = semantic_chunking(text_segment) 
                    
                    if not segment_chunks_text:
                        continue
                    
                    for chunk_text_from_segment in segment_chunks_text:
                        if not chunk_text_from_segment.strip(): # Ensure chunk itself is not empty
                            continue
                        chunk_vector = encode_text(chunk_text_from_segment)
                        if chunk_vector is None:
                            print_warning(f"Could not encode chunk from {file_props['filename']} ({location_str}). Skipping.")
                            continue
                        
                        chunk_full_props = {
                            "chunk_text": chunk_text_from_segment,
                            "chunk_index": current_file_chunk_idx, # Overall index within the file
                            "file_id": canvas_file_id, 
                            "course_id": course_id,
                            "file_name": file_props["filename"],
                            "source_location": location_str # Store the page/slide/para info
                        }
                        
                        # Weaviate UUID for the chunk, ensuring uniqueness within the file
                        chunk_uuid = generate_uuid5(f'{canvas_file_id}_{current_file_chunk_idx}', "Chunk")
                        all_chunks_to_insert_with_vectors.append(
                            {"properties": chunk_full_props, "vector": chunk_vector.tolist(), "uuid": chunk_uuid}
                        )
                        current_file_chunk_idx += 1
            else:
                 print_status(f"File type '{file_extension}' for '{file_props['filename']}' is not supported for text chunking. Only metadata inserted/updated.")
                    
    if len(files_collection.batch.failed_objects) > 0:
        print_warning(f"Failed to import {len(files_collection.batch.failed_objects)} file objects for course {course_id}.")
    else:
        print_status(f"Successfully inserted/updated file metadata for course {course_id}.")

    # Batch insert all collected chunks
    if all_chunks_to_insert_with_vectors:
        chunks_collection = client.collections.get("Chunk")
        with chunks_collection.batch.dynamic() as chunk_batch:
            for item in all_chunks_to_insert_with_vectors:
                chunk_batch.add_object(
                    properties=item["properties"],
                    vector=item["vector"],
                    uuid=item["uuid"]
                )
        if len(chunks_collection.batch.failed_objects) > 0:
            print_warning(f"Failed to import {len(chunks_collection.batch.failed_objects)} chunk objects for course {course_id}.")
        else:
            print_status(f"Successfully inserted {len(all_chunks_to_insert_with_vectors)} chunk objects for course {course_id}.")
    else:
        print_status(f"No chunks were prepared for insertion for course {course_id}.")


def pull_files_from_weaviate(client, course_id: int):
    """
    Pulls files objects from Weaviate and saves them to the local filesystem.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        course_id (int): ID of the course to which the files belong.
    """
    # Get the course collection
    collection = client.collections.get("File")

    # Get the course object
    try:
        response = collection.query.fetch_objects(
            filters=wq.Filter.by_property("course_id").equal(course_id) # Use wq.Filter
        )
        return response.objects
    except Exception as e:
        print_warning(f"Error pulling files from Weaviate for course {course_id}: {e}")
        return []


def verify_objects_in_collection(client, collection_name: str):
    """
    Displays uuid and properties of 'collection_name' collection.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        collection_name (str): The Weaviate client collection name.
    """
    try:

        collection = client.collections.get(collection_name)    
        
        for item in collection.iterator():
            print_status(f"UUID: {item.uuid}, Properties: {item.properties}")
    except Exception as e:
        print_warning(f"Error querying collection '{collection_name}': {e}")


def search_weaviate(client, query_text: str, course_id: int = None, limit: int = 10, alpha_hybrid: float = 0.5, context_window: int = 1):
    """
    Performs a search in the Weaviate "Chunk" collection.
    Can perform a hybrid search or a pure vector search based on alpha_hybrid.
    Retrieves context chunks around the primary matches.

    Args:
        client: The Weaviate client.
        query_text: The text to search for.
        course_id: Optional course ID to filter by.
        limit: The number of primary results to return from the initial search.
        alpha_hybrid: The alpha value for hybrid search (0 for keyword, 1 for vector, 0.5 for balanced).
        context_window: Number of chunks before and after each primary match to retrieve as context.
                       Set to 0 to disable context retrieval.

    Returns:
        A list of Weaviate result objects (hydrated with properties), sorted by file_id and chunk_index.
    """
    if not client or not client.is_ready():
        print_warning("Weaviate client not connected or not ready for search.")
        return []

    try:
        chunks_collection = client.collections.get("Chunk")
        
        filters = None
        if course_id is not None:
            filters = Filter.by_property("course_id").equal(course_id)

        print_status(f"Searching for '{query_text}' with limit {limit}, course_id {course_id}, context_window {context_window}")

        # Generate query vector since the collection has no built-in vectorizer
        query_vector = encode_text(query_text)
        if query_vector is None:
            print_warning(f"Could not generate vector for query: {query_text}")
            return []

        # Perform initial search (hybrid or vector)
        initial_response = chunks_collection.query.hybrid(
            query=query_text,
            vector=query_vector.tolist(),
            alpha=alpha_hybrid, # 0 (keyword) to 1 (vector)
            limit=limit,
            filters=filters,
        )
        
        initial_matches = initial_response.objects
        if not initial_matches:
            print_status("No primary matches found.")
            return []

        if context_window == 0:
            print_status(f"Context window is 0, returning {len(initial_matches)} primary matches.")
            return initial_matches 

        all_relevant_chunks_map = {} # Use UUID as key to remove duplicates

        # Add primary matches and fetch context
        for matched_chunk in initial_matches:
            if matched_chunk.uuid not in all_relevant_chunks_map:
                all_relevant_chunks_map[matched_chunk.uuid] = matched_chunk
            
            # Fetch context for this matched_chunk
            try:
                original_file_id = matched_chunk.properties.get('file_id')
                original_chunk_index = matched_chunk.properties.get('chunk_index')

                if original_file_id is None or original_chunk_index is None:
                    print_warning(f"Skipping context for chunk {matched_chunk.uuid} due to missing file_id or chunk_index.")
                    continue

                for i in range(1, context_window + 1):
                    # Previous chunks
                    prev_chunk_idx_to_find = original_chunk_index - i
                    if prev_chunk_idx_to_find >= 0:
                        neighbor_filters_prev = Filter.all_of([
                            Filter.by_property("file_id").equal(original_file_id),
                            Filter.by_property("chunk_index").equal(prev_chunk_idx_to_find)
                        ])
                        if course_id is not None: # Add course_id filter if specified for main query
                            if neighbor_filters_prev.filters is None: # Should not happen with Filter.all_of
                                neighbor_filters_prev.filters = []
                            neighbor_filters_prev.filters.append(Filter.by_property("course_id").equal(course_id))
                            
                        neighbor_response_prev = chunks_collection.query.fetch_objects(
                            filters=neighbor_filters_prev,
                            limit=1
                        )
                        if neighbor_response_prev.objects:
                            prev_neighbor = neighbor_response_prev.objects[0]
                            if prev_neighbor.uuid not in all_relevant_chunks_map:
                                all_relevant_chunks_map[prev_neighbor.uuid] = prev_neighbor
                    
                    # Next chunks
                    next_chunk_idx_to_find = original_chunk_index + i
                    neighbor_filters_next = Filter.all_of([
                        Filter.by_property("file_id").equal(original_file_id),
                        Filter.by_property("chunk_index").equal(next_chunk_idx_to_find)
                    ])
                    if course_id is not None: # Add course_id filter
                        neighbor_filters_next.filters.append(Filter.by_property("course_id").equal(course_id))

                    neighbor_response_next = chunks_collection.query.fetch_objects(
                        filters=neighbor_filters_next,
                        limit=1
                    )
                    if neighbor_response_next.objects:
                        next_neighbor = neighbor_response_next.objects[0]
                        if next_neighbor.uuid not in all_relevant_chunks_map:
                             all_relevant_chunks_map[next_neighbor.uuid] = next_neighbor
            except Exception as e_context:
                print_warning(f"Error fetching context for chunk {matched_chunk.uuid}: {e_context}")


        # Sort all collected chunks (primary + context) by file_id and then chunk_index
        final_sorted_chunks = sorted(
            list(all_relevant_chunks_map.values()),
            key=lambda c: (c.properties.get('file_id', float('inf')), c.properties.get('chunk_index', float('inf')))
        )
        
        print_status(f"Returning {len(final_sorted_chunks)} chunks (primary matches + context), sorted.")
        return final_sorted_chunks

    except Exception as e:
        print_warning(f"Error during search in Weaviate: {e}")
        return []
    
    
def generate_prompt_for_llm(query_text: str, search_results: list, max_context_chunks: int = 5):
    """
    Generates a prompt string for a large language model (LLM) like Gemini,
    including the user's query and context from search results.

    Args:
        query_text (str): The original user query.
        search_results (list): A list of Weaviate result objects (chunks).
        max_context_chunks (int): The maximum number of search result chunks to include in the context.

    Returns:
        str: The generated prompt string.
    """
    if not search_results:
        prompt = f"""User Question: {query_text}

        No relevant context was found in the documents for this question.
        Please answer the user's question based on your general knowledge, or state if you cannot answer it without specific context.
        """
        print("--- Generated LLM Prompt (No Context) ---")
        print(prompt)
        print("----------------------------------------")
        return prompt

    context_str_parts = ["Context from relevant documents:"]
    for i, res_obj in enumerate(search_results[:max_context_chunks]):
        try:
            chunk_text = res_obj.properties.get('chunk_text', 'N/A')
            file_name = res_obj.properties.get('file_name', 'Unknown File')
            source_loc = res_obj.properties.get('source_location', 'Location N/A') 
            
            context_str_parts.append("---")
            context_str_parts.append(f"Source Document: {file_name} ({source_loc})") 
            context_str_parts.append("Content:")
            context_str_parts.append(chunk_text)
        except Exception as e:
            print_warning(f"Error processing search result for prompt generation: {e}")
            context_str_parts.append("---")
            context_str_parts.append("[Error processing one of the context chunks]")

    context_str = "\n".join(context_str_parts)

    prompt = f"""User Question: {query_text}

    {context_str}
    ---

    Instructions for the AI:
    Based *only* on the context provided above from the documents, please do not answer the user question but rather provide what source document or 
    documnets and then the page or slide number that give you the answer and what the content is. Do not mention which chunk the answer is from. state the sections that best answer the question first.
    If the context does not contain enough information to answer the question, clearly state that the information is not available in the provided documents.
    Do not use any external knowledge or information outside of the provided document excerpts.
    Be concise and directly address what context can answer the user's question.
    """

    print("\n--- Generated LLM Prompt ---")
    print(prompt)
    print("----------------------------\n")
    return prompt
