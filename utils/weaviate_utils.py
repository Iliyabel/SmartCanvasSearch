import weaviate
import weaviate.classes as wvc


# Initialize and return a weaviate client.
def create_client(url="http://localhost:8080"):
    try:
        # client = WeaviateClient.init(
        #     url=url
        # )

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
            wvc.config.Property(name="name", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="quarter", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="instructor", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="courseCode", data_type=wvc.config.DataType.TEXT),
        ],
        description="A Canvas course with relevant metadata",
    )


    schema.create(
        name="File",
        properties=[
            wvc.config.Property(name="fileName", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="fileType", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="uploadDate", data_type=wvc.config.DataType.DATE),
            wvc.config.Property(name="fullText", data_type=wvc.config.DataType.TEXT),
            #wvc.config.Property(name="belongsTo", data_type=wvc.config.DataType.REFERENCE, target_collection="Course"),
        ],
        description="A file belonging to a course",
    )
    

    schema.create(
        name="Chunk",
        vectorizer_config="none",
        properties=[
            wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="chunkIndex", data_type=wvc.config.DataType.INT),
            wvc.config.Property(name="embedding", data_type=wvc.config.DataType.VECTOR),
            #wvc.config.Property(name="sourceFile", data_type=DataType.REFERENCE, target_collection="File"),
        ],
        description="A chunk of text from a file used for vector search",
    )

    print("Schema created successfully!")


# Deletes schema. For debugging.
def delete_schema(client):
    client.collections.delete(client.collections.Course)
    print("Schema deleted.")