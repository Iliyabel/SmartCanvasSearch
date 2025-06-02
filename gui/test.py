import sys
import os
# import json
from utils import general_utils as gu
from dotenv import load_dotenv

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, 
    QGraphicsDropShadowEffect, QStackedWidget, QGridLayout
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
        self.buttons_layout.setSpacing(15)
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
        self.user_input.returnPressed.connect(self.handle_user_message)
        self.bottom_input_layout.addWidget(self.user_input, 1)

        self.run_button = QPushButton("Run")
        self.run_button.setObjectName("run_button")
        self.run_button.setGraphicsEffect(shadow3)
        self.run_button.clicked.connect(self.handle_user_message)
        self.bottom_input_layout.addWidget(self.run_button)

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

    def handle_user_message(self):
        user_text = self.user_input.text().strip()
        if user_text:
            self.add_message_to_chat("You", user_text, True)
            self.user_input.clear()
            # Placeholder for bot response logic
            QTimer.singleShot(500, lambda: self.add_bot_message(f"Thinking about: '{user_text[:30]}...'"))


    def add_bot_message(self, message):
        self.add_message_to_chat("Bot", message, False)


class MainWindow(QMainWindow): # Renamed from ChatWindow
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Course Compass")
        self.setGeometry(500, 100, 1000, 900)
        self.setWindowIcon(QIcon("resources/icon.png"))
        self.canvas_token = None # To store the token

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.welcome_screen = WelcomeScreen()
        self.course_selection_screen = CourseSelectionScreen()
        self.chat_screen = ChatScreenWidget()

        self.stacked_widget.addWidget(self.welcome_screen)           # Index 0
        self.stacked_widget.addWidget(self.course_selection_screen) # Index 1
        self.stacked_widget.addWidget(self.chat_screen)           # Index 2

        self.welcome_screen.token_submitted.connect(self.handle_token_submission)
        self.course_selection_screen.course_selected.connect(self.handle_course_selection)
        self.chat_screen.back_to_courses_button.clicked.connect(self.show_course_selection_screen)
        
        self.check_existing_token_and_load() # Check for canvas token at startup
        
    def check_existing_token_and_load(self):
        """Checks for an existing token and tries to load courses, skipping WelcomeScreen if successful."""
        saved_token_path = os.path.join(PROJECT_ROOT_GUI, "resources", "canvas_token.txt")
        token = None
        
        if os.path.exists(saved_token_path):
            try:
                with open(saved_token_path, "r") as f:
                    token = f.read().strip()
                if token:
                    print("Found saved token. Attempting to load courses automatically.")
                    self.canvas_token = token # Store 
                else:
                    print("Saved token file is empty.")
                    token = None 
            except IOError as e:
                print(f"Error reading saved token: {e}")
                token = None

        if token: # If token successfully read from the file
            # Load .env for BASE_URL
            dotenv_path = os.path.join(PROJECT_ROOT_GUI, ".env")
            
            if os.path.exists(dotenv_path):
                load_dotenv(dotenv_path)
                print(f"Loaded .env file from: {dotenv_path}")
            else:
                print(f"Warning: .env file not found at {dotenv_path}. Cannot auto-fetch classes.")
                self.show_welcome_screen() # Failed, display welcome screen
                return

            BASE_URL = os.getenv("BASE_URL")
            if not BASE_URL:
                print("Error: BASE_URL not found for auto-fetch. Please configure .env.")
                self.show_welcome_screen() # Failed, display welcome screen
                return

            headers = {"Authorization": f"Bearer {token}"}
            print("MainWindow: Auto-fetching classes with saved token...")
            result = gu.getAllClasses(BASE_URL, headers) # Updates ClassList.json
            
            if result == "Successful":
                print("MainWindow: Auto-fetched and saved class list successfully.")
            else:
                print("MainWindow: Failed to auto-fetch class list with saved token.")
            
            # Load courses into the selection screen
            self.course_selection_screen.load_and_display_courses()
            self.show_course_selection_screen() # Skips the WelcomeScreen
        else:
            # Error reading it
            print("No valid saved token found. Displaying Welcome Screen.")
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

    def handle_course_selection(self, course_name):
        # Might want to use self.canvas_token here to interact with Canvas API
        print(f"Selected course: {course_name} (using token: {'Token Present' if self.canvas_token else 'No Token'})")
        self.chat_screen.set_selected_course(course_name)
        self.show_chat_screen()

