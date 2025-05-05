import weaviate
import weaviate.classes.config as wvcc
from weaviate.classes.config import Property, DataType, ReferenceProperty
from weaviate.util import generate_uuid5
import json
import os
from tqdm import tqdm
from general_utils import extractTextFromPdf, extractTextFromPPTX, extractTextFromDocx, extractTextFromTxt, semantic_chunking, downloadCourseFile
from dotenv import load_dotenv



# Initialize and return a weaviate client.
def create_client(url="http://localhost:8080"):
    try:
        client = weaviate.connect_to_local()

        if client.is_ready() and client.is_live():
            print(f"Connected to Weaviate at {url}")
            return client
        else:
            raise Exception("Weaviate is not live/ready")
    except Exception as e:
        print("Connection error:", str(e))
        return None


# Creates the weaviate schema
def create_schema(client):
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
            Property(name="course_code", data_type=DataType.TEXT),
            Property(name="start_date", data_type=DataType.DATE),
            Property(name="end_date", data_type=DataType.DATE),
            Property(name="uuid", data_type=DataType.TEXT),
            
        ],
        description="A Canvas course with relevant metadata",
        vectorizer_config=wvcc.Configure.Vectorizer.none(),
        # MAYBE ADD REFERENCE WHILE INSERTING FILES
        # references=[
        #     ReferenceProperty(
        #         name="hasFiles",
        #         target_collection="File"
        #     )
        # ]
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
            Property(name="course_uuid", data_type=DataType.TEXT),
        ],
        description="A file belonging to a course",
        ##### MAYBE ADD REFERENCE WHILE INSERTING FILES ####
        # references=[
        #     ReferenceProperty(
        #         name="fromCourse",
        #         target_collection="Course"
        #     ),
        # ]
    )
    

    # Add Chunk collection to schema
    schema.create(
        name="Chunk",
        vectorizer_config=wvcc.Configure.Vectorizer.none(),
        properties=[
            Property(name="uuid", data_type=DataType.TEXT),
            Property(name="chunk_text", data_type=DataType.TEXT),
            Property(name="chunk_index", data_type=DataType.INT),
            Property(name="chunk_vector", data_type=DataType.INT_ARRAY),
            Property(name="file_uuid", data_type=DataType.TEXT),
            Property(name="course_uuid", data_type=DataType.TEXT),
            #Property(name="sourceFile", data_type=DataType.REFERENCE, target_collection="File"),
        ],
        description="A chunk of text from a file used for vector search",
    )

    print("Schema created successfully!")


# Deletes schema. For debugging.
def delete_schema(client):
    client.collections.delete_all()
    print("Schema deleted.")


def prepare_courses_for_weaviate(json_file_path):
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
                    "course_code": course["course_code"],
                    "start_date": course["start_at"],
                    "end_date": course["end_at"],
                    "uuid": course["uuid"]
                })

                # Check if a directory with the course UUID exists
                course_directory = os.path.join("Courses", course["uuid"])
                if not os.path.exists(course_directory):
                    os.makedirs(course_directory)
                    print(f"Created directory for course UUID: {course['uuid']}")
        

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
    

def prepare_files_for_weaviate(json_file_path, course_uuid):
    """
    Extracts file data from a JSON file and prepares it for insertion into a Weaviate database.

    Args:
        json_file_path (str): Path to the JSON file containing file data.
        course_uuid (str): UUID of the course to which the files belong.    
        
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
                    "course_uuid": course_uuid
                })

                # Check if the course directory exists
                course_directory = os.path.join("Courses", course_uuid)
        
                load_dotenv()  # Load environment variables from .env file

                API_TOKEN = os.getenv("API_KEY")
                BASE_URL = os.getenv("BASE_URL")
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


def prepare_chunks_for_weaviate(chunks, course_uuid, source_file):
    """
    Prepares chunk data for insertion into a Weaviate database.

    Args:
        chunks (list): List of chunk strings.
        course_uuid (str): UUID of the course to which the chunks belong.
        source_file (str): The source file name.

    Returns:
        list: A list of dictionaries containing prepared chunk data.
    """
    prepared = []
    for idx, chunk in enumerate(chunks):
        prepared.append({
            "uuid": generate_uuid5(chunk),
            "chunk_text": chunk,
            "chunk_index": idx,
            "source_file": source_file,
            "course_uuid": course_uuid
        })
    return prepared


def insert_courses_into_weaviate(client, json_file_path):
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

    courses_collection = client.collections.get("Course")

    with courses_collection.batch.dynamic() as batch:
        for course in tqdm(courses):
            
            # Add course object
            batch.add_object(
                properties={
                    "name": course["name"],
                    "course_code": course["course_code"],
                    "start_date": course["start_date"],
                    "end_date": course["end_date"],
                    "uuid": course["uuid"]
                },
            )

        # Check for failed objects
    if len(courses_collection.batch.failed_objects) > 0:
        print(f"Failed to import {len(courses_collection.batch.failed_objects)} course objects")


def insert_files_into_weaviate(client, json_file_path, course_uuid):
    """
    Reads file data from a JSON file, prepares it, and inserts it into the Weaviate database.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        json_file_path (str): Path to the JSON file containing file data.
        course_uuid (str): UUID of the course to which the files belong.
    """
    # Prepare the file data
    files = prepare_files_for_weaviate(json_file_path, course_uuid)

    if not files:
        print("No files to insert.")
        return

    files_collection = client.collections.get("File")

    with files_collection.batch.dynamic() as batch:
        for file in tqdm(files):
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
                        "course_uuid": course_uuid
                    },
                )
                print(f"Inserted file: {file['display_name']}")
            except Exception as e:
                print(f"Failed to insert file {file['display_name']}: {e}")


def insert_text_chunks_into_weaviate(client, course_uuid, file_uuid):
    """
    Reads a text-based file, extracts text, chunks it semantically,
    and inserts the chunks into the Weaviate database.

    Args:
        client (weaviate.Client): The Weaviate client instance.
        text_file_path (str): Path to the text-based file.
        course_uuid (str): UUID of the course to which the chunks belong.
    """
    # Path to the text file
    text_file_path = "Courses/1714841_files1.json"  # Example path, replace with actual path

    # Determine extraction method based on file type
    file_extension = text_file_path.split('.')[-1].lower()
    
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

    # Optional: prepare chunks for insertion
    prepared_chunks = prepare_chunks_for_weaviate(chunks, course_uuid, file_uuid)

    chunks_collection = client.collections.get("Chunk")

    with chunks_collection.batch.dynamic() as batch:
        for chunk in tqdm(prepared_chunks):
            try:
                batch.add_object(
                    properties={
                        "chunk_text": chunk["chunk_text"],
                        "chunk_index": chunk["chunk_index"],
                        "chunk_vector": chunk["chunk_vector"],
                        "file_uuid": chunk["source_file"],
                        "course_uuid": chunk["course_uuid"]
                    },
                    uuid=chunk["uuid"]
                )
                print(f"Inserted chunk {chunk['chunk_index']} from {chunk['source_file']}")
            except Exception as e:
                print(f"Failed to insert chunk {chunk['chunk_index']} from {chunk['source_file']}: {e}")


def verify_objects_in_collection(client, collection_name):
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