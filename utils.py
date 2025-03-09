import json
import requests


# Function to read in config file data
def read_config(file_path):
    with open(file_path, 'r') as file:
        config_data = json.load(file)
    return config_data


# Function to get list of 10 classes
def get10ClassList(BASE_URL, headers):
    # Get list of courses
    response = requests.get(f'{BASE_URL}courses', headers=headers)

    # Check if request was successful
    if response.status_code == 200:
        courses = response.json()
        with open("ClassList10.json", "w") as file:
            json.dump(courses, file, indent=4)  
        return "Successful"
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return "ERROR"
    

# Function to get list of all classes
def getAllClasses(BASE_URL, headers):
    # Get list of courses
    response = requests.get(f'{BASE_URL}courses?per_page=100', headers=headers)

    # Check if request was successful
    if response.status_code == 200:
        courses = response.json()
        with open("ClassList.json", "w") as file:
            json.dump(courses, file, indent=4)  
        return "Successful"
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return "ERROR"