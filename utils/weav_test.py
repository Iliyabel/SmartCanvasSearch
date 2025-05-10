from weaviate_utils import create_client, create_schema, insert_courses_into_weaviate, verify_objects_in_collection, insert_files_into_weaviate, generate_uuid5
from cprint import print_header

print("")
print_header("START -- Weaviate test script")

client = create_client()

if client:
    try:
        create_schema(client)
        # insert_courses_into_weaviate(client, "resources/ClassList.json")
        #verify_objects_in_collection(client, "Course")


        # insert_files_into_weaviate(client, "Courses/1714841/files1.json", 1714841)    
        # verify_objects_in_collection(client, "File")


        # print("file id: 114175019. has uuid: " + generate_uuid5("114175019"))
        # print("Course id: 1714841. has uuid: " + generate_uuid5("1714841"))

    finally:
        client.close()

print_header("END -- Weaviate test script")
print("")