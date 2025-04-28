from weaviate_utils import create_client, create_schema, delete_schema, insert_courses_into_weaviate

client = create_client()

if client:
    try:
        create_schema(client)
        insert_courses_into_weaviate(client, "resources/ClassList.json")
    finally:
        client.close()

