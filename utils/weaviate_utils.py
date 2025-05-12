import weaviate
import weaviate.classes.config as wvcc
from weaviate.classes.config import Property, DataType, ReferenceProperty
from weaviate.classes.query import Filter
import weaviate.classes.query as wq
from weaviate.util import generate_uuid5
import json
import os
from general_utils import extractTextFromPdf, extractTextFromPPTX, extractTextFromDocx, extractTextFromTxt, semantic_chunking, downloadCourseFile, encode_text
import nltk
from dotenv import load_dotenv
from cprint import print_header, print_status, print_warning

nltk.download('punkt_tab')

# Initialize and return a weaviate client.
def create_client(url="http://localhost:8080"):
    try:
        client = weaviate.connect_to_local()

        if client.is_ready() and client.is_live():
            print_status(f"Connected to Weaviate at {url}")
            return client
        else:
            raise Exception("Weaviate is not live/ready")
    except Exception as e:
        print_warning("Connection error:", str(e))
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
    if "Course" in schema.list_all().keys():
        print("Schema already exists. Skipping creation.")
        return
    
    # Add Course collection to schema
    schema.create(
        name="Course",
        properties=[
            Property(name="name", data_type=DataType.TEXT),
            Property(name="course_id", data_type=DataType.INT),
            Property(name="course_code", data_type=DataType.TEXT),
            Property(name="start_date", data_type=DataType.DATE),
            Property(name="end_date", data_type=DataType.DATE),
            Property(name="uuid", data_type=DataType.TEXT),
            
        ],
        description="A Canvas course with relevant metadata",
        vectorizer_config=wvcc.Configure.Vectorizer.none(),
    )


    # Add File collection to schema
    schema.create(
        name="File",
        properties=[
            Property(name="file_id", data_type=DataType.INT),
            Property(name="uuid", data_type=DataType.TEXT),
            Property(name="display_name", data_type=DataType.TEXT),
            Property(name="file_type", data_type=DataType.TEXT),
            Property(name="file_path", data_type=DataType.TEXT),
            Property(name="url", data_type=DataType.TEXT),
            Property(name="size_bytes", data_type=DataType.INT),
            Property(name="created_at", data_type=DataType.DATE),
            Property(name="modified_at", data_type=DataType.DATE),
            Property(name="filename", data_type=DataType.TEXT),
            Property(name="course_id", data_type=DataType.INT),
        ],
        description="A file belonging to a course",
        vectorizer_config=wvcc.Configure.Vectorizer.none(),
    )
    

    # Add Chunk collection to schema
    schema.create(
        name="Chunk",
        properties=[
            Property(name="chunk_text", data_type=DataType.TEXT),
            Property(name="chunk_index", data_type=DataType.INT),
            Property(name="file_id", data_type=DataType.INT),
            Property(name="course_id", data_type=DataType.INT),
        ],
        description="A chunk of text from a file used for vector search",
        vectorizer_config=wvcc.Configure.Vectorizer.none(),
    )

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
        with open(json_file_path, 'r') as file:
            courses = json.load(file)

        print(f"Loaded {len(courses)} courses from {json_file_path}")

        # Extract relevant fields
        prepared_data = []
        for course in courses:
            if all(key in course for key in ["name", "course_code", "start_at", "end_at", "uuid"]):
                prepared_data.append({
                    "name": course["name"],
                    "course_id": course["id"],
                    "course_code": course["course_code"],
                    "start_date": course["start_at"],
                    "end_date": course["end_at"],
                    "uuid": course["uuid"]
                })

                # Check if a directory with the course UUID exists
                course_directory = os.path.join("Courses", str(course["id"]))
                if not os.path.exists(course_directory):
                    os.makedirs(course_directory)
                    print(f"Created directory for course id: {course['id']}")
        

        return prepared_data
    
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_file_path}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    

def prepare_files_for_weaviate(json_file_path: str, course_id: int):
    """
    Extracts file data from a JSON file and prepares it for insertion into a Weaviate database.

    Args:
        json_file_path (str): Path to the JSON file containing file data.
        course_id (int): ID of the course to which the files belong.    
        
    Returns:
        list: A list of dictionaries containing extracted file data.
    """
    try:
        # Load the JSON data
        with open(json_file_path, 'r') as file:
            files = json.load(file)

        print(f"Loaded {len(files)} files from {json_file_path}")

        # Extract relevant fields
        prepared_data = []
        for file in files:
            if all(key in file for key in ["id", "display_name", "url", "size", "created_at", "filename"]):
                prepared_data.append({
                    "file_id": file["id"],
                    "uuid": file["uuid"],
                    "display_name": file["display_name"],
                    "file_type": file["mime_class"],
                    "file_path": file["url"],
                    "url": file["url"],
                    "size_bytes": file["size"],
                    "created_at": file["created_at"],
                    "modified_at": file["modified_at"],
                    "filename": file["filename"],
                    "course_id": course_id
                })

                # Check if the course directory exists
                course_directory = os.path.join("Courses", str(course_id))
        
                load_dotenv()  # Load environment variables from .env file

                API_TOKEN = os.getenv("API_KEY")
                headers = {
                    'Authorization': f'Bearer {API_TOKEN}'
                }

                # Download the file into the course directory
                file_path = os.path.join(course_directory, file["filename"])
                try:
                    downloadCourseFile(file["filename"], file["url"], file_path, headers)

                    print(f"Downloaded file {file['filename']} to {course_directory}")
                except Exception as e:
                    print(f"Failed to download file {file['filename']}: {e}")

        return prepared_data

    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_file_path}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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


def insert_courses_into_weaviate(client, json_file_path: str):
    """
    Reads course data from a JSON file, prepares it, and inserts it into the Weaviate database.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        json_file_path (str): Path to the JSON file containing course data.
    """
    # Prepare the course data
    courses = prepare_courses_for_weaviate(json_file_path)

    if not courses:
        print("No courses to insert.")
        return

    # Get the Course collection
    courses_collection = client.collections.get("Course")

    # Go through each course and add it to the collection
    with courses_collection.batch.dynamic() as batch:
        for course in courses:
            
            # Add course object
            batch.add_object(
                properties={
                    "name": course["name"],
                    "course_id": course["course_id"],
                    "course_code": course["course_code"],
                    "start_date": course["start_date"],
                    "end_date": course["end_date"],
                    "uuid": course["uuid"]
                },
                uuid=generate_uuid5(course["course_id"])
            )

        # Check for failed objects
    if len(courses_collection.batch.failed_objects) > 0:
        print(f"Failed to import {len(courses_collection.batch.failed_objects)} course objects")


def insert_files_into_weaviate(client, json_file_path: str, course_id: int):
    """
    Reads file data from a JSON file, prepares it, and inserts it into the Weaviate database.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        json_file_path (str): Path to the JSON file containing file data.
        course_id (int): ID of the course to which the files belong.
    """
    # Prepare the file data
    files = prepare_files_for_weaviate(json_file_path, course_id)

    if not files:
        print("No files to insert.")
        return

    # Get the File collection
    files_collection = client.collections.get("File")

    # Go through each file and add it to the collection
    with files_collection.batch.dynamic() as batch:
        for file in files:
            # Check if the file type is supported
            if file["file_type"] in ["pdf", "ppt", "doc", "text"]:
                try:
                    # Add file object
                    batch.add_object(
                        properties={
                            "file_id": file["file_id"],
                            "uuid": file["uuid"],
                            "display_name": file["display_name"],
                            "file_type": file["file_type"],
                            "file_path": file["file_path"],
                            "url": file["url"],
                            "size_bytes": file["size_bytes"],
                            "created_at": file["created_at"],
                            "modified_at": file["modified_at"],
                            "filename": file["filename"],
                            "course_id": course_id
                        },
                        uuid=generate_uuid5(file["file_id"])
                    )
                    print(f"Inserted file: {file['display_name']}")
                except Exception as e:
                    print(f"Failed to insert file {file['display_name']}: {e}")

                # chunk the text and insert chunk into Weaviate
                try:
                    # Insert text chunks into Weaviate
                    insert_text_chunks_into_weaviate(client, course_id, file["display_name"])

                except Exception as e:
                    print(f"Failed to insert file {file['display_name']}: {e}")


def insert_text_chunks_into_weaviate(client, course_id: int, file_name: str, file_id: int):
    """
    Reads a text-based file, extracts text, chunks it semantically,
    and inserts the chunks into the Weaviate database.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        course_id (int): ID of the course to which the file belongs.
        file_name (str): Name of file.
        file_id (int): ID of the file.
    """
    # Path to the text file
    text_file_path = f'Courses/{course_id}/{file_name}'

    # Determine extraction method based on file type
    file_extension = text_file_path.split('.')[-1].lower()


    # Extract text from the file
    text = ""
    
    try:
        if file_extension == 'pdf':
            text = extractTextFromPdf(text_file_path)
        elif file_extension == 'pptx':
            text = extractTextFromPPTX(text_file_path)
        elif file_extension == 'docx':
            text = extractTextFromDocx(text_file_path)
        elif file_extension == 'txt':
            text = extractTextFromTxt(text_file_path)
        else:
            print(f"Unsupported file type: {file_extension}")
            return
    except Exception as e:
        print(f"Failed to extract text from {text_file_path}: {e}")
        return

    if not text.strip():
        print("No text extracted to insert.")
        return


    # Perform semantic chunking
    chunks = semantic_chunking(text)

    if not chunks:
        print("No chunks created from the text.")
        return

    # Prepare chunks for insertion
    prepared_chunks = prepare_chunks_for_weaviate(chunks)

    # Get the Chunk collection
    chunks_collection = client.collections.get("Chunk")

    # Go through each chunk and add it to the collection
    with chunks_collection.batch.dynamic() as batch:
        for chunk in prepared_chunks:
            try:
                batch.add_object(
                    properties={
                        "chunk_text": chunk["chunk_text"],
                        "chunk_index": chunk["chunk_index"],
                        "file_id": file_id,
                        "course_id": course_id,
                        "file_name": file_name
                    },
                    uuid=generate_uuid5(chunk["chunk_index"] + file_id),
                    vector=encode_text(chunk["chunk_text"])
                )
                print(f"Inserted chunk {chunk['chunk_index']} from {file_name}")
            except Exception as e:
                print(f"Failed to insert chunk {chunk['chunk_index']} from {file_name}: {e}")


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
    files_response = collection.query.fetch_objects(
        filters=Filter.by_property("course_id").equal(course_id)
    )

    # Check if the course exists
    if not files_response:
        print(f"Course with ID {course_id} not found.")
        return

    return files_response.objects


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
            print(item.uuid, item.properties)
    except Exception as e:
        print(f"Error querying the database: {e}")


def search_weaviate(client, query: str, collection_name: str):
    """
    Searches for a query in the specified Weaviate collection.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        query (str): The search query.
        collection_name (str): The name of the collection to search in.

    Returns:
        list: A list of search results.
    """
    try:
        # Get the collection
        collection = client.collections.get(collection_name)

        # Encode the query into a vector embedding
        querty_vector = encode_text(query)

        results = collection.query.near_vector(near_vector=querty_vector, limit=5,  return_metadata=wq.MetadataQuery(distance=True))
        return results
    except Exception as e:
        print(f"Error querying the database: {e}")
        return []
