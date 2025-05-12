import weaviate_utils as wu
from cprint import print_header

print("")
print_header("START -- Weaviate test script")

client = wu.create_client()

if client:
    try:
        wu.create_schema(client)
        # wu.insert_courses_into_weaviate(client, "resources/ClassList.json")
        #wu.verify_objects_in_collection(client, "Course")


        ################TESTING FILES######################
        # objects = wu.pull_files_from_weaviate(client, 1714841)

        # print(f"Found {len(objects)} files")
        # for file_obj in objects:
        #     print(f"File id: {file_obj.properties.get("file_id")}")
        #     print(f"Filename: {file_obj.properties.get('filename')}")
        #     print("---")
        ###################################################


        # wu.insert_files_into_weaviate(client, "Courses/1714841/files1.json", 1714841)    
        # wu.verify_objects_in_collection(client, "File")


        ############### Testing chunks ######################

        wu.insert_text_chunks_into_weaviate(client, 1714841, "1_CreateTeam.docx", 114175018)
        
        # text = wu.extractTextFromDocx("Courses/1714841/1_CreateTeam.docx")
        # chunks = wu.semantic_chunking(text)

        # for i, chunk in enumerate(chunks):
        #     print(f"Chunk {i+1}: {chunk} encoding: {wu.encode_text(chunk)}")

        # wu.verify_objects_in_collection(client, "Chunk")



    finally:
        client.close()

print_header("END -- Weaviate test script")
print("")