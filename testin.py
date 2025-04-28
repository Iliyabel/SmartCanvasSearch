from utils import *


json_file_path = "resources/ClassList.json"  # Adjust the path as needed
courses_data = prepare_courses_for_weaviate(json_file_path)

# Print the extracted data
for course in courses_data:
    print(course)