from utils import *


with open("resources/ClassList.json") as f:
    class_list = json.load(f)

print(load_courses(class_list))