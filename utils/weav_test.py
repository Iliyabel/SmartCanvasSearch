from weaviate_utils import create_client, create_schema, delete_schema

client = create_client()

if client:
    create_schema(client)
    #delete_schema(client)
    client.close()

