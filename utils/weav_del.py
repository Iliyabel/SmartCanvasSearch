from weaviate_utils import create_client, create_schema, delete_schema

client = create_client()

if client:
    try:
        delete_schema(client)
    finally:
        client.close()