import os
from utils import general_utils as gu
from utils.weaviate_manager import WeaviateManager
from utils.ai_utils import get_gemini_response, get_dummy_ai_response, format_ai_response
from utils.weaviate_utils import generate_prompt_for_llm
import threading 
from dotenv import load_dotenv

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, 
    QGraphicsDropShadowEffect, QStackedWidget, QGridLayout, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

# Determine project root from gui/test.py's location
SCRIPT_DIR_GUI = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_GUI = os.path.dirname(SCRIPT_DIR_GUI)


class WelcomeScreen(QWidget):
    token_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.overall_layout = QVBoxLayout(self)
        self.overall_layout.setContentsMargins(50, 35, 50, 35) # Margins for the whole screen

        shadow = QGraphicsDropShadowEffect(blurRadius=6, xOffset=0, yOffset=0)
        shadow1 = QGraphicsDropShadowEffect(blurRadius=4, xOffset=0, yOffset=0)
        shadow2 = QGraphicsDropShadowEffect(blurRadius=4, xOffset=0, yOffset=2)

        title_label = QLabel("Welcome to Course Compass!")
        title_label.setObjectName("welcome_title") 
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overall_layout.addWidget(title_label)

        # ScrollArea for the instructional content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        scroll_area.setGraphicsEffect(shadow) # Add shadow effect to scroll area

        # Container widget for the scrollable content
        scroll_content_widget = QWidget()
        scroll_content_widget.setObjectName("welcome_scroll_widget")
        self.content_layout = QVBoxLayout(scroll_content_widget) 
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Content starts at top of scroll
        self.content_layout.setSpacing(10) 
        self.content_layout.setContentsMargins(20, 20, 20, 0)
        
        # --- Instructions using QLabels ---
        info_widgets = []

        p1 = QLabel("<b>Course Compass</b> helps you navigate your Canvas course materials efficiently.")
        p1.setObjectName("instruction_paragraph")
        p1.setTextFormat(Qt.TextFormat.RichText)
        p1.setWordWrap(True)
        info_widgets.append(p1)

        p2 = QLabel("To get started, you'll need a <b>Canvas Access Token</b>.")
        p2.setObjectName("instruction_paragraph")
        p2.setTextFormat(Qt.TextFormat.RichText)
        p2.setWordWrap(True)
        info_widgets.append(p2)

        h3 = QLabel("<h3>How to get your Canvas Access Token:</h3>")
        h3.setObjectName("instruction_heading")
        h3.setTextFormat(Qt.TextFormat.RichText) # Allows HTML for heading
        h3.setWordWrap(True)
        info_widgets.append(h3)
        
        instructions_list = [
            "Log in to your Canvas account.",
            "Go to <b>Account</b> (usually in the left sidebar).",
            "Click on <b>Settings</b>.",
            "Scroll down to the <b>Approved Integrations</b> section.",
            "Click on <b>+ New Access Token</b>.",
            "For <b>Purpose</b>, you can enter something like \"Course Compass App\".",
            "Leave <b>Expires</b> blank for no expiration, or set a date.",
            "Click <b>Generate Token</b>.",
            "<b>Important:</b> Copy the generated token immediately. You won't be able to see it again."
        ]

        for i, item_text in enumerate(instructions_list):
            item_label = QLabel(f"{i+1}. {item_text}")
            item_label.setObjectName("instruction_list_item")
            item_label.setTextFormat(Qt.TextFormat.RichText) 
            item_label.setWordWrap(True)
            item_label.setAlignment(Qt.AlignmentFlag.AlignLeft) # Align list items left
            info_widgets.append(item_label)

        p_enter_token = QLabel("Enter your token below to proceed.")
        p_enter_token.setObjectName("instruction_paragraph_final")
        p_enter_token.setWordWrap(True)
        info_widgets.append(p_enter_token)

        for widget in info_widgets:
            widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
            self.content_layout.addWidget(widget)
            
        self.content_layout.addStretch(1) # Pushes content up within scroll area if it's short
        scroll_area.setWidget(scroll_content_widget)
        self.overall_layout.addWidget(scroll_area, 1)
        # --- End of Instructions ---


        self.token_input_layout = QHBoxLayout()
        self.token_input_layout.setContentsMargins(0, 20, 0, 0)
        
        token_label = QLabel("Canvas Access Token:")
        token_label.setObjectName("token_label")
        self.token_input = QLineEdit()
        self.token_input.setObjectName("token_input_welcome")
        self.token_input.setPlaceholderText("Paste your token here")
        self.token_input.setGraphicsEffect(shadow1) # Add shadow effect
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password) # Hide token input
        self.token_input_layout.addWidget(token_label)
        self.token_input_layout.addWidget(self.token_input, 1)
        self.overall_layout.addLayout(self.token_input_layout)

        self.submit_button = QPushButton("Continue with Token")
        self.submit_button.setObjectName("submit_token_button") 
        self.submit_button.setGraphicsEffect(shadow2)
        self.submit_button.clicked.connect(self.on_submit)
        self.overall_layout.addWidget(self.submit_button, 0, Qt.AlignmentFlag.AlignCenter)
        

    def on_submit(self):
        token = self.token_input.text().strip()
        
        if not token:
            # Show an error message if token is empty
            error_label = self.findChild(QLabel, "error_label_token")
            if not error_label:
                error_label = QLabel("Please enter a valid Canvas Access Token.")
                error_label.setObjectName("error_label_token") 
                index_of_token_layout = self.overall_layout.indexOf(self.token_input_layout)
                self.overall_layout.insertWidget(index_of_token_layout, error_label, 0, Qt.AlignmentFlag.AlignCenter)
            error_label.setVisible(True)
            return

        # Hide error message if it was visible
        error_label = self.findChild(QLabel, "error_label_token")
        if error_label:
            error_label.setVisible(False)

        # 1. Save the token to resources/canvas_token.txt
        resources_dir = os.path.join(PROJECT_ROOT_GUI, "resources")
        if not os.path.exists(resources_dir):
            os.makedirs(resources_dir)
            print(f"Created directory: {resources_dir}")
        
        token_file_path = os.path.join(resources_dir, "canvas_token.txt")
        try:
            with open(token_file_path, "w") as f:
                f.write(token)
            print(f"Canvas token saved to: {token_file_path}")
        except IOError as e:
            print(f"Error saving token to file: {e}")
        
        # 2. Load BASE_URL from .env file
        dotenv_path = os.path.join(PROJECT_ROOT_GUI, ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            print(f"Loaded .env file from: {dotenv_path}")
        else:
            print(f"Warning: .env file not found at {dotenv_path}. Cannot fetch classes.")
            self.token_submitted.emit(token) # Still emit to move to next screen, but classes won't be fresh
            return

        BASE_URL = os.getenv("BASE_URL")

        if not BASE_URL:
            print("Error: BASE_URL not found in .env file or environment variables.")
            self.token_submitted.emit(token) # Still emit
            return
        
        # 3. Call getAllClasses
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print("Attempting to fetch all classes...")
        result = gu.getAllClasses(BASE_URL, headers)
        if result == "Successful":
            print("Successfully fetched and saved class list.")
        else:
            print("Failed to fetch class list.")

        self.token_submitted.emit(token)


class CourseSelectionScreen(QWidget):
    # dict: {'course_id': int, 'course_name': str}
    course_selected = pyqtSignal(dict) # Signal to emit when a course is selected.

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(50, 35, 50, 35)

        shadow = QGraphicsDropShadowEffect(blurRadius=6, xOffset=0, yOffset=0) # Shadow for scroll area

        title_label = QLabel("Select a Course")
        title_label.setObjectName("course_selection_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)

        # --- Scroll Area for Course Buttons ---
        self.scroll_area_courses = QScrollArea()
        self.scroll_area_courses.setWidgetResizable(True)
        self.scroll_area_courses.setGraphicsEffect(shadow) # Add shadow effect to scroll area
        self.scroll_area_courses.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.scroll_content_courses_widget = QWidget() # Widget to hold the grid layout
        self.scroll_content_courses_widget.setObjectName("scroll_content_courses_widget")
        self.buttons_layout = QGridLayout(self.scroll_content_courses_widget) # Grid layout for buttons
        self.buttons_layout.setSpacing(20)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Load courses data from JSON file
        self.courses_data = []
        self.no_courses_label = QLabel("Fetching courses or no courses found.\nPlease submit a token if you haven't.") # Initial message
        self.no_courses_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttons_layout.addWidget(self.no_courses_label, 0, 0, 1, 2) 
        self.no_courses_label.setVisible(True) 
        
        self.scroll_area_courses.setWidget(self.scroll_content_courses_widget)
        self.layout.addWidget(self.scroll_area_courses, 1) # Scroll area takes expanding space
        # --- End of Scroll Area for Course Buttons ---


    def load_and_display_courses(self):
        """Loads courses from ClassList.json and populates the buttons."""
        # Clear previous buttons and the "no courses" label
        while self.buttons_layout.count():
            item = self.buttons_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.courses_data = [] # Reset
        try:
            # Path to ClassList.json relative to the project root
            json_file_path = os.path.join(PROJECT_ROOT_GUI, "resources", "ClassList.json")
            
            if not os.path.exists(json_file_path):
                print(f"CourseSelectionScreen: ClassList.json not found at {json_file_path}. Cannot load courses.")
                self.courses_data = []
            else:
                self.courses_data = gu.extract_course_name_id_pairs(json_file_path)
                print(f"CourseSelectionScreen: Loaded {len(self.courses_data)} courses for selection.")

        except Exception as e:
            print(f"Error loading courses in CourseSelectionScreen: {e}")
            self.courses_data = [] 
        
        if not self.courses_data:
            self.no_courses_label = QLabel("No courses found or failed to load.\nEnsure ClassList.json is populated and accessible.")
            self.no_courses_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.buttons_layout.addWidget(self.no_courses_label, 0, 0, 1, 2)
            self.no_courses_label.setVisible(True)
        else:
            self.no_courses_label.setVisible(False) # Hide if courses are found
            row, col = 0, 0
            max_cols = 2
            for course_info in self.courses_data:
                course_name = course_info.get("name", "Unnamed Course")
                button = QPushButton(course_name)
                button.setObjectName("course_button")
                shadow1 = QGraphicsDropShadowEffect(blurRadius=4, xOffset=0, yOffset=2)
                button.setGraphicsEffect(shadow1)
                button.setMinimumHeight(50)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                button.clicked.connect(lambda checked=False, c_info=course_info: self.course_button_clicked(c_info))
                self.buttons_layout.addWidget(button, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def course_button_clicked(self, course_name):
        self.course_selected.emit(course_name)


class ChatMessageWidget(QWidget):
    """
    A widget to display a single chat message with a sender title and the message content.
    """
    def __init__(self, sender_name, message_text, is_user_message):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 2, 5, 2) # Reduced margins for tighter packing
        self.layout.setSpacing(2) # Spacing between title and message

        self.message_label = QLabel(message_text)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Set Labels based on whether it's a user message or bot message
        if is_user_message:
            self.sender_label = QLabel(sender_name)
            self.sender_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.sender_label.setObjectName("user_title")
            self.message_label.setObjectName("user_message")
            self.layout.addWidget(self.sender_label, alignment=Qt.AlignmentFlag.AlignRight)
            self.layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            # Icon label
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(50, 50)
            self.icon_label.setScaledContents(True)
            self.icon_label.setPixmap(QIcon("resources/icon.png").pixmap(50, 50))
            
            self.message_label.setObjectName("bot_message")
            self.message_label.setTextFormat(Qt.TextFormat.RichText)
            self.layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignLeft)
            self.layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Ensure the message label can expand vertically
        self.message_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)


class ChatScreenWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(50, 35, 50, 35)
        self.main_layout.setSpacing(10)

        # Define shadow effect
        shadow0 = QGraphicsDropShadowEffect(blurRadius=4, xOffset=0, yOffset=2) # Shadow for back button
        shadow1 = QGraphicsDropShadowEffect(blurRadius=6, xOffset=0, yOffset=0) # Shadow for scroll area
        shadow2 = QGraphicsDropShadowEffect(blurRadius=6, xOffset=0, yOffset=0) # Shadow for input area
        shadow3 = QGraphicsDropShadowEffect(blurRadius=4, xOffset=0, yOffset=2) # shadow for Run button

        self.header_layout = QHBoxLayout()
        self.selected_course_label = QLabel("No course selected")
        self.selected_course_label.setObjectName("selected_course_label")
        self.selected_course_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.back_to_courses_button = QPushButton("Change Course")
        self.back_to_courses_button.setObjectName("back_to_courses_button")
        self.back_to_courses_button.setGraphicsEffect(shadow0)

        self.header_layout.addWidget(self.selected_course_label, 1, Qt.AlignmentFlag.AlignLeft)
        self.header_layout.addWidget(self.back_to_courses_button, 0, Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(self.header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setGraphicsEffect(shadow1)

        self.chat_container_widget = QWidget()
        self.chat_container_widget.setObjectName("chat_container_widget")
        self.chat_container_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.chat_layout = QVBoxLayout(self.chat_container_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(8)

        self.scroll_area.setWidget(self.chat_container_widget)
        self.main_layout.addWidget(self.scroll_area, 1)

        self.bottom_input_widget = QWidget()
        self.bottom_input_widget.setObjectName("bottom_input_widget")
        self.bottom_input_widget.setGraphicsEffect(shadow2)
        self.bottom_input_layout = QHBoxLayout(self.bottom_input_widget)
        self.bottom_input_layout.setContentsMargins(0, 20, 0, 0)
        self.bottom_input_layout.setSpacing(8)

        self.user_input = QLineEdit()
        self.user_input.setObjectName("user_input")
        self.user_input.setPlaceholderText("Enter a question...")
        self.user_input.setFont(QFont("Arial", 10))
        self.bottom_input_layout.addWidget(self.user_input, 1)

        self.run_button = QPushButton("Run")
        self.run_button.setObjectName("run_button")
        self.run_button.setGraphicsEffect(shadow3)
        self.bottom_input_layout.addWidget(self.run_button)
        
        self.run_button.clicked.connect(lambda: self.parent().parent().handle_user_message())
        self.user_input.returnPressed.connect(lambda: self.parent().parent().handle_user_message())

        self.main_layout.addWidget(self.bottom_input_widget, 0, Qt.AlignmentFlag.AlignBottom)

    def set_selected_course(self, course_name):
        self.selected_course_label.setText(course_name['name'])
        # Clear previous chat history if any, or load course-specific history
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.add_bot_message("Welcome to the Course Compass!")
        self.add_bot_message("Please ask a question about your course materials.")


    def add_message_to_chat(self, sender_name, message_text, is_user):
        if not message_text.strip():
            return
        message_widget = ChatMessageWidget(sender_name, message_text, is_user)
        
        alignment_container = QWidget()
        alignment_layout = QHBoxLayout(alignment_container)
        alignment_layout.setContentsMargins(0,0,0,0)

        if is_user:
            alignment_layout.addStretch(1)
            alignment_layout.addWidget(message_widget, 0, Qt.AlignmentFlag.AlignTop)
        else:
            alignment_layout.addWidget(message_widget, 0, Qt.AlignmentFlag.AlignTop)
            alignment_layout.addStretch(1)
        
        self.chat_layout.addWidget(alignment_container)
        QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def add_bot_message(self, message):
        self.add_message_to_chat("Bot", message, False)


class MainWindow(QMainWindow): 
    # Signal for Weaviate status updates to show in GUI
    weaviate_status_update = pyqtSignal(str)
    
    # Signal for chat messages from threads
    chat_message_ready = pyqtSignal(str, str, bool) # sender_name, message_text, is_user
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Course Compass")
        self.setGeometry(500, 100, 1000, 900)
        
        icon_path = os.path.join(PROJECT_ROOT_GUI, "resources", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Warning: Main window icon not found at {icon_path}")
            
        self.canvas_token = None # To store the token
        self.gemini_api_key = None # To store the Gemini API key
        self.selected_course_data = None 
        self.base_url = None # Store base_url

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.welcome_screen = WelcomeScreen()
        self.course_selection_screen = CourseSelectionScreen(self)
        self.chat_screen = ChatScreenWidget(self)

        self.stacked_widget.addWidget(self.welcome_screen)           # Index 0
        self.stacked_widget.addWidget(self.course_selection_screen) # Index 1
        self.stacked_widget.addWidget(self.chat_screen)           # Index 2

        self.welcome_screen.token_submitted.connect(self.handle_token_submission)
        self.course_selection_screen.course_selected.connect(self.handle_course_selection)
        self.chat_screen.back_to_courses_button.clicked.connect(self.show_course_selection_screen)
        
        self.weaviate_manager = WeaviateManager(project_root=PROJECT_ROOT_GUI)
        self.weaviate_initialized_for_session = False # Flag to init only once per session
        
        self.weaviate_status_update.connect(self.update_status_bar)
        self.chat_message_ready.connect(self._add_message_to_chat_slot)
        
        self._load_env_vars() # Load .env once
        self.check_existing_token_and_load() # Check for canvas token at startup
        
    def _load_env_vars(self):
        """Loads BASE_URL from .env file."""
        dotenv_path = os.path.join(PROJECT_ROOT_GUI, ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            self.base_url = os.getenv("BASE_URL")
            if self.base_url:
                print(f"Loaded BASE_URL from .env: {self.base_url}")
            else:
                print("Warning: BASE_URL not found in .env file.")
                
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not self.gemini_api_key:
                print("[WARNING] GEMINI_API_KEY not found in .env file. AI responses will not be available.")
        else:
            print(f"Warning: .env file not found at {dotenv_path}.")
            
    def closeEvent(self, event):
        """Handle window close event."""
        print("MainWindow closing. Shutting down Weaviate service if managed...")
        self.weaviate_manager.close_connection() # Close client connection first
        self.weaviate_manager.stop_service() # Stop docker-compose
        event.accept()

    def _initialize_weaviate_if_needed(self):
        """Starts Weaviate service, connects client, and ensures schema. Threaded."""
        if self.weaviate_initialized_for_session:
            if not self.weaviate_manager.client or not self.weaviate_manager.client.is_ready():
                # Attempt to reconnect if client lost connection
                self.weaviate_status_update.emit("Reconnecting to Weaviate...")
                if not self.weaviate_manager.connect_client():
                    self.weaviate_status_update.emit("Failed to reconnect Weaviate client.")
                    return False
                self.weaviate_status_update.emit("Reconnected to Weaviate.")
            return True 

        self.weaviate_status_update.emit("Starting Weaviate service...")
        if not self.weaviate_manager.start_service():
            self.weaviate_status_update.emit("Failed to start Weaviate Docker service.")
            return False
        self.weaviate_status_update.emit("Weaviate service started. Connecting client...")

        if not self.weaviate_manager.connect_client():
            self.weaviate_status_update.emit("Failed to connect Weaviate client.")
            return False
        self.weaviate_status_update.emit("Weaviate client connected. Ensuring schema...")

        if not self.weaviate_manager.ensure_schema():
            self.weaviate_status_update.emit("Failed to ensure Weaviate schema.")
            return False
        
        self.weaviate_status_update.emit("Weaviate schema OK. Initializing course metadata...")
        
        # Ingest all courses metadata (from ClassList.json) once per session
        class_list_path = os.path.join(PROJECT_ROOT_GUI, "resources", "ClassList.json")
        if os.path.exists(class_list_path):
            if not self.weaviate_manager.ingest_all_courses_metadata(class_list_path):
                self.weaviate_status_update.emit("Failed to ingest all courses metadata.")
        else:
            self.weaviate_status_update.emit("ClassList.json not found, cannot ingest all courses metadata.")

        self.weaviate_initialized_for_session = True
        self.weaviate_status_update.emit("Weaviate initialized and ready for course data.")
        return True

    def _run_weaviate_init_threaded(self):
        thread = threading.Thread(target=self._initialize_weaviate_if_needed, daemon=True)
        thread.start()

    def _ingest_course_data_threaded(self, course_id):
        def ingest_task():
            self.weaviate_status_update.emit(f"Starting data ingestion for course ID: {course_id}...")
            if self.weaviate_manager.ingest_course_files_and_chunks(course_id):
                self.weaviate_status_update.emit(f"Successfully ingested data for course ID: {course_id}.")
            else:
                self.weaviate_status_update.emit(f"Failed to ingest data for course ID: {course_id}.")
        
        # Ensure Weaviate is initialized before ingesting specific course data
        if not self.weaviate_initialized_for_session:
            if not self._initialize_weaviate_if_needed(): # This is blocking if called directly
                 print("Cannot ingest course data: Weaviate initialization failed.")
                 return
        
        thread = threading.Thread(target=ingest_task, daemon=True)
        thread.start()
        
    def check_existing_token_and_load(self):
        """Checks for an existing token and tries to load courses, skipping WelcomeScreen if successful."""
        saved_token_path = os.path.join(PROJECT_ROOT_GUI, "resources", "canvas_token.txt")
        token = None
        if os.path.exists(saved_token_path):
            try:
                with open(saved_token_path, "r") as f:
                    token = f.read().strip()
                if token:
                    print("Found saved token.")
                    self.canvas_token = token 
                else:
                    print("Saved token file is empty.")
                    token = None 
            except IOError as e:
                print(f"Error reading saved token: {e}")
                token = None

        if token and self.base_url: # Check for both token and base_url
            headers = {"Authorization": f"Bearer {token}"}
            print("MainWindow: Auto-fetching classes with saved token...")
            result = gu.getAllClasses(self.base_url, headers) 
            
            if result == "Successful":
                print("MainWindow: Auto-fetched and saved class list successfully.")
            else:
                print("MainWindow: Failed to auto-fetch class list with saved token.")
            
            self.course_selection_screen.load_and_display_courses()
            self.show_course_selection_screen() 
        else:
            if not token:
                print("No valid saved token found.")
            if not self.base_url:
                print("BASE_URL not configured.")
            print("Displaying Welcome Screen.")
            self.show_welcome_screen()

    def show_welcome_screen(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_course_selection_screen(self):
        self.stacked_widget.setCurrentIndex(1)
            
    def show_chat_screen(self):
        self.stacked_widget.setCurrentIndex(2)
        
    def handle_token_submission(self, token):
        self.canvas_token = token
        print(f"Canvas Token Stored: {'*' * len(token)}")
        self.course_selection_screen.load_and_display_courses() # Call the refresh method
        self.show_course_selection_screen()

    def handle_course_selection(self, course_data: dict):
        self.selected_course_data = course_data
        course_name = course_data.get("name", "Unknown Course")
        course_id = course_data.get("id")

        print(f"Selected course: {course_name} (ID: {course_id})")

        if course_id is None:
            print("Error: Course ID is missing. Cannot fetch materials.")
            return

        if not self.canvas_token or not self.base_url:
            print("Error: Canvas token or BASE_URL is not available. Cannot fetch materials.")
            self.show_welcome_screen()
            return

        headers = {"Authorization": f"Bearer {self.canvas_token}"}

        # --- Perform file operations ---
        self.weaviate_status_update.emit(f"Downloading files for course ID: {course_id}...") # GUI feedback
        print(f"Fetching file list for course ID: {course_id}...")
        list_result = gu.listCourseMaterial(course_id, self.base_url, headers)

        if list_result == "Successful":
            print(f"Successfully got file list for course {course_id}. Now downloading materials...")
            # Download specific file types
            gu.getCoursePPTXMaterial(course_id, headers)
            gu.getCoursePDFMaterial(course_id, headers)
            gu.getCourseDOCXMaterial(course_id, headers)
            gu.getCourseTXTMaterial(course_id, headers)
            self.weaviate_status_update.emit(f"File download complete for course ID: {course_id}.")
            print(f"Finished attempting to download materials for course {course_id}.")

            # --- Weaviate operations ---        
            self._ingest_course_data_threaded(course_id)
            
        else:
            self.weaviate_status_update.emit(f"Failed to get file list for course {course_id}. Skipping downloads and Weaviate.")
            print(f"Failed to get file list for course {course_id}. Skipping material download and Weaviate ops.")

        self.chat_screen.set_selected_course(course_data)
        self.show_chat_screen()
    
    def handle_user_message(self): 
        user_text = self.chat_screen.user_input.text().strip()
        if user_text and self.selected_course_data:
            course_id = self.selected_course_data.get("id")
            
            # Add user's message to chat UI 
            self.chat_screen.add_message_to_chat("You", user_text, True)
            self.chat_screen.user_input.clear() # Clear input field 
            
            # Perform search in a thread
            def search_task():
                self.weaviate_status_update.emit(f"Searching for: '{user_text}'...")
                
                search_limit = 5 # Number of primary results
                search_context_window = 1 # Neighbors for each primary result
                
                results = self.weaviate_manager.search_chunks(
                    user_text, 
                    course_id=course_id, 
                    limit=search_limit, 
                    context_window=search_context_window
                ) 

                llm_max_chunks = search_limit * (1 + 2 * search_context_window) 
                generated_prompt = generate_prompt_for_llm(user_text, results if results else [], max_context_chunks=llm_max_chunks)

                # Check if gemini_api_key is set
                if not self.gemini_api_key:
                    self.weaviate_status_update.emit("AI response unavailable (API key missing). Prompt printed to console.")
                    return 
                
                if not generated_prompt:
                    self.weaviate_status_update.emit("Failed to generate prompt for AI.")
                    return
                
                self.weaviate_status_update.emit("Getting AI response...")

                try:
                    ai_response_text = get_gemini_response(generated_prompt, self.gemini_api_key, model_name="gemini-2.0-flash-lite")
                    # ai_response_text = get_dummy_ai_response()
                    print(f"[AI_RESPONSE] {ai_response_text}") # Print AI response to console for debugging
                    ai_response_text = format_ai_response(ai_response_text)
                    
                    # Display AI response in chat
                    self.chat_message_ready.emit("Gemini AI", ai_response_text, False)
                    self.weaviate_status_update.emit("AI response received.")
                    
                except Exception as e:
                    # Fallback, get_gemini_response should return error strings
                    error_msg = f"Error processing AI response: {e}"
                    print(f"[GUI_ERROR] {error_msg}") # Or your app's error printing
                    self.chat_message_ready.emit("System Error", error_msg, False)
                    self.weaviate_status_update.emit("Error getting AI response.")


            search_thread = threading.Thread(target=search_task, daemon=True)
            search_thread.start()
            
    def _add_message_to_chat_slot(self, sender_name: str, message_text: str, is_user: bool):
        """This slot runs in the main GUI thread and safely updates the chat."""
        if self.chat_screen: # Ensure chat_screen exists
            self.chat_screen.add_message_to_chat(sender_name, message_text, is_user)
            
    def update_status_bar(self, message: str):
        """Updates the QStatusBar with the given message."""
        if self.status_bar:
            self.status_bar.showMessage(message, 7000) # Show message for 7 seconds 
            print(f"[STATUS_BAR] {message}")
