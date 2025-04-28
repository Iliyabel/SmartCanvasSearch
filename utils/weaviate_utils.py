import weaviate
import weaviate.classes as wvc
import weaviate.classes.config as wvcc
from weaviate.classes.config import Property, DataType, ReferenceProperty
import json
import os
from tqdm import tqdm

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
    

    schema.create(
        name="Course",
        properties=[
            Property(name="name", data_type=DataType.TEXT),
            Property(name="course_code", data_type=DataType.TEXT),
            Property(name="start_date", data_type=DataType.TEXT),
            Property(name="end_date", data_type=DataType.TEXT),
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


    schema.create(
        name="File",
        properties=[
            Property(name="fileName", data_type=DataType.TEXT),
            Property(name="fileType", data_type=DataType.TEXT),
            Property(name="uploadDate", data_type=DataType.DATE),
            Property(name="fullText", data_type=DataType.TEXT),
            #Property(name="belongsTo", data_type=wvcc.DataType.REFERENCE, target_collection="Course"),
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
    

    schema.create(
        name="Chunk",
        vectorizer_config=wvcc.Configure.Vectorizer.none(),
        properties=[
            Property(name="text", data_type=DataType.TEXT),
            Property(name="chunkIndex", data_type=DataType.INT),
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

    # # Insert each course into Weaviate
    # for course in courses:
    #     try:
    #         client.data.create(
    #             data_object=course,
    #             class_name="Course"
    #         )
    #         print(f"Inserted course: {course['name']}")
    #     except Exception as e:
    #         print(f"Failed to insert course {course['name']}: {e}")

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
