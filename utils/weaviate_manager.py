import subprocess
import time
import os
from . import weaviate_utils as wu

def print_manager_status(msg): print(f"[WM_STATUS] {msg}")
def print_manager_warning(msg): print(f"[WM_WARNING] {msg}")
def print_manager_error(msg): print(f"[WM_ERROR] {msg}")

class WeaviateManager:
    def __init__(self, project_root: str, docker_compose_file: str = "docker-compose.yml"):
        self.project_root = project_root
        self.docker_compose_path = os.path.join(project_root, docker_compose_file)
        self.client = None
        self.service_started_by_manager = False

    def _run_docker_compose(self, args: list) -> bool:
        try:
            # Ensure docker-compose is run from the directory containing the yml file
            process = subprocess.Popen(
                ["docker-compose", "-f", self.docker_compose_path] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_root # Set working directory
            )
            stdout, stderr = process.communicate(timeout=120)
            
            if process.returncode == 0:
                print_manager_status(f"Docker-compose {' '.join(args)} successful.")
                return True
            else:
                print_manager_error(f"Docker-compose {' '.join(args)} failed. Return code: {process.returncode}")
                print_manager_error(f"Stderr: {stderr.decode()}")
                print_manager_error(f"Stdout: {stdout.decode()}")
                return False
        except FileNotFoundError:
            print_manager_error("Error: docker-compose command not found. Is Docker Desktop running and docker-compose installed/in PATH?")
            return False
        except subprocess.TimeoutExpired:
            print_manager_error(f"Docker-compose {' '.join(args)} timed out.")
            process.kill()
            return False
        except Exception as e:
            print_manager_error(f"Exception running docker-compose {' '.join(args)}: {e}")
            return False

    def start_service(self, retries=3, delay=10) -> bool:
        """Starts the Weaviate Docker service if not already running."""
        print_manager_status("Attempting to start Weaviate service via docker-compose...")
        if not os.path.exists(self.docker_compose_path):
            print_manager_error(f"docker-compose.yml not found at {self.docker_compose_path}")
            return False

        if self._run_docker_compose(["up", "-d"]): # Detached mode
            self.service_started_by_manager = True
            print_manager_status("Docker-compose up -d command issued. Waiting for Weaviate to be ready...")
            
            # Wait and check readiness
            for i in range(retries):
                time.sleep(delay)
                temp_client = wu.create_client()
                if temp_client and temp_client.is_ready():
                    print_manager_status("Weaviate service is up and ready.")
                    temp_client.close()
                    return True
                elif temp_client:
                    temp_client.close() # Close if connected but not ready
                print_manager_warning(f"Weaviate not ready yet (attempt {i+1}/{retries}). Retrying in {delay}s...")
            print_manager_error("Weaviate service did not become ready after multiple attempts.")
            return False
        return False

    def stop_service(self) -> bool:
        """Stops the Weaviate Docker service if it was started by this manager."""
        if self.service_started_by_manager:
            print_manager_status("Attempting to stop Weaviate service via docker-compose down...")
            if self._run_docker_compose(["down"]):
                self.service_started_by_manager = False
                return True
            return False
        else:
            print_manager_status("Weaviate service was not started by this manager or already stopped, skip docker-compose down.")
            return True 

    def connect_client(self) -> bool:
        if self.client and self.client.is_ready():
            print_manager_status("Already connected to Weaviate.")
            return True
        
        self.client = wu.create_client()
        if self.client:
            return True
        print_manager_error("Failed to connect Weaviate client.")
        return False

    def ensure_schema(self) -> bool:
        if not self.client:
            print_manager_warning("Cannot ensure schema: Weaviate client not connected.")
            return False
        try:
            wu.create_schema(self.client)
            return True
        except Exception as e:
            print_manager_error(f"Error creating/verifying Weaviate schema: {e}")
            return False

    def ingest_all_courses_metadata(self, class_list_json_path: str) -> bool:
        if not self.client:
            print_manager_warning("Cannot ingest courses: Weaviate client not connected.")
            return False
        
        print_manager_status(f"Preparing courses from: {class_list_json_path}")
        courses_data = wu.prepare_courses_for_weaviate(class_list_json_path)
        if courses_data:
            print_manager_status(f"Ingesting {len(courses_data)} courses into Weaviate...")
            wu.insert_courses_into_weaviate(self.client, courses_data)
            return True
        else:
            print_manager_warning("No course data prepared for ingestion.")
            return False

    def ingest_course_files_and_chunks(self, course_id: int) -> bool:
        if not self.client:
            print_manager_warning(f"Cannot ingest files for course {course_id}: Weaviate client not connected.")
            return False

        files_json_path = os.path.join(self.project_root, "Courses", str(course_id), "files.json")
        if not os.path.exists(files_json_path):
            print_manager_error(f"Files JSON for course {course_id} not found at {files_json_path}")
            return False

        print_manager_status(f"Preparing files for course {course_id} from: {files_json_path}")
        
        files_data = wu.prepare_files_for_weaviate(files_json_path, course_id, self.project_root)
        
        if files_data:
            print_manager_status(f"Ingesting {len(files_data)} files and their chunks for course {course_id}...")
            wu.insert_files_into_weaviate(self.client, files_data, course_id)
            return True
        else:
            print_manager_warning(f"No file data prepared for ingestion for course {course_id}.")
            return False
            
    def search_chunks(self, query_text: str, course_id: int = None, limit: int = 5) -> list:
        if not self.client:
            print_manager_warning("Cannot search: Weaviate client not connected.")
            return []
        return wu.search_weaviate(self.client, query_text, course_id=course_id, limit=limit)

    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None
            print_manager_status("Weaviate client connection closed.")