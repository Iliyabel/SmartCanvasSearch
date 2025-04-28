from weaviate_utils import create_client, create_schema, delete_schema, insert_courses_into_weaviate, verify_objects_in_collection

client = create_client()

if client:
    try:
        create_schema(client)
        #insert_courses_into_weaviate(client, "resources/ClassList.json")
        verify_objects_in_collection(client, "Course")
    finally:
        client.close()

