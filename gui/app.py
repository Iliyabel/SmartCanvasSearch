import sys
import json
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QStackedWidget,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor


# --- Configuration ---
TOKEN_FILE = "canvas_token.txt" # File to store the Canvas token


# --- Backend Placeholder Functions ---
def save_token(token):
    """Saves the token to a file."""
    try:
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        return True
    except IOError:
        print(f"Error: Could not save token to {TOKEN_FILE}")
        return False


def load_token():
    """Loads the token from a file."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                return f.read().strip()
        except IOError:
            print(f"Error: Could not read token from {TOKEN_FILE}")
            return None
    return None


def fetch_canvas_courses(api_token):
    """
    Placeholder function to simulate fetching Canvas courses.
    In a real application, this would call function to make backend call.
    """
    print(f"Attempting to fetch courses with token: {api_token[:5]}...") # Print only first 5 chars for security
    if not api_token or len(api_token) < 10: # Basic validation
        return {"status": "error", "message": "Invalid or missing API token.", "courses": []}

    # Dummy data for now:
    dummy_courses = [
        {"id": 101, "name": "Introduction to Python Programming"},
        {"id": 102, "name": "Calculus I"},
        {"id": 103, "name": "Art History 101"},
        {"id": 104, "name": "Advanced Quantum Physics"},
    ]
    return {"status": "success", "message": "Courses fetched successfully (simulated).", "courses": dummy_courses}


class WelcomeScreen(QWidget):
    """
    A welcome screen that provides instructions on how to obtain a Canvas Access Token.
    This screen is displayed when the application starts.
    """
    token_submitted = pyqtSignal(str) # Signal emitted when token is submitted

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(300, 100, 300, 100)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Welcome to Course Compass!")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setContentsMargins(0, 0, 0, 30)
        layout.addWidget(title_label)

        # Introduction Text
        intro_text = (
            "This program helps you interact with your Canvas courses.\n"
            "To get started, you'll need a Canvas Access Token."
        )
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)
        intro_label.setFont(QFont("Arial", 12))
        layout.addWidget(intro_label)

        # Token Instructions
        instructions_title = QLabel("How to get your Canvas Access Token:")
        instructions_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(instructions_title)

        instructions_text = (
            "1. Log in to your Canvas instance (e.g., yourschool.instructure.com).\n"
            "2. In the global navigation menu on the left, click 'Account'.\n"
            "3. Click 'Settings'.\n"
            "4. Scroll down to the 'Approved Integrations' section.\n"
            "5. Click the '+ New Access Token' button.\n"
            "6. For 'Purpose', you can type something like 'Course Query App'.\n"
            "7. Leave 'Expires' blank for no expiration, or set a date.\n"
            "8. Click 'Generate Token'.\n"
            "9. **Important:** Copy the generated token immediately. You won't be able to see it again.\n"
            "10. Paste the token in the field below."
        )
        instructions_label = QLabel(instructions_text)
        instructions_label.setWordWrap(True)
        instructions_label.setFont(QFont("Arial", 11))
        layout.addWidget(instructions_label)

        # Token Input
        token_layout = QHBoxLayout()
        token_label = QLabel("Canvas Access Token:")
        token_label.setFont(QFont("Arial", 12))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Paste your token here")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password) # Hide token
        self.token_input.setFont(QFont("Arial", 11))
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        layout.addLayout(token_layout)

        # Status Label (for errors or success messages)
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: red;") # Default to error color
        layout.addWidget(self.status_label)

        # Save Button
        self.save_button = QPushButton("Save Token and Continue")
        self.save_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.on_save_clicked)
        layout.addWidget(self.save_button)

        layout.addStretch() # Pushes content to the top


    def on_save_clicked(self):
        token = self.token_input.text().strip()
        if not token:
            self.status_label.setText("Please enter an access token.")
            self.status_label.setStyleSheet("color: red;")
            return

        if save_token(token):
            self.status_label.setText("Token saved successfully!")
            self.status_label.setStyleSheet("color: green;")
            self.token_submitted.emit(token) # Emit signal with the token
        else:
            self.status_label.setText("Failed to save token. Check console for errors.")
            self.status_label.setStyleSheet("color: red;")


class ChatbotScreen(QWidget):
    """
    A screen that displays the chatbot interface.
    This screen is displayed after the user has entered their Canvas Access Token.
    """
    course_selected = pyqtSignal(dict) # Signal emitted when a course is selected

    def __init__(self):
        super().__init__()
        self.courses = []
        self.init_ui()


    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15) # Increased spacing for bubbles

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", 12))
        # General styling for the chat display area itself
        self.chat_display.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px;")
        self.main_layout.addWidget(self.chat_display, 1) # Give chat display more stretch factor

        # Area for course selection buttons (or other inputs)
        self.input_area_container = QWidget()
        self.input_area_layout = QVBoxLayout(self.input_area_container)
        self.input_area_layout.setContentsMargins(0,0,0,0)
        self.input_area_layout.setSpacing(10)

        # Scroll area for course buttons if there are many
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame) # No border for the scroll area itself
        self.scroll_area.setWidget(self.input_area_container)
        self.scroll_area.setFixedHeight(150) # Adjust as needed
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.main_layout.addWidget(self.scroll_area)

        # --- Input area at the bottom ---
        self.bottom_input_widget = QWidget()
        self.bottom_input_layout = QHBoxLayout(self.bottom_input_widget)
        self.bottom_input_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_input_layout.setSpacing(8)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter a question...")
        self.user_input.setMinimumHeight(38)
        self.user_input.setStyleSheet("""
            border-radius: 16px;
            border: 1px solid #ced4da;
            padding: 8px 14px;
            font-size: 12pt;
            background: white;
            color: #606060;
        """)
        self.bottom_input_layout.addWidget(self.user_input, 1)

        self.run_button = QPushButton("Run")
        self.run_button.setMinimumHeight(38)
        self.run_button.setMinimumWidth(80)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #188038;
                color: white;
                border-radius: 16px;
                padding: 0 24px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4BA173; }
            QPushButton:pressed { background-color: #145c2c; }
        """)
        self.run_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.run_button.clicked.connect(self.handle_user_message)
        self.bottom_input_layout.addWidget(self.run_button)

        self.main_layout.addWidget(self.bottom_input_widget, 0, Qt.AlignmentFlag.AlignBottom)

        # Back to Welcome Screen button
        self.back_button = QPushButton("Back to Token Setup")
        self.back_button.setStyleSheet("""
                QPushButton {
                    background-color: #62967a; color: white; border-radius: 6px; padding: 8px;
                    border: none;
                }
                QPushButton:hover { background-color: #4BA173; }
                QPushButton:pressed { background-color: #188038; }
            """)
        self.back_button.setFont(QFont("Arial", 10))
        # self.back_button.clicked.connect(self.go_back) # Connection will be set in MainWindow
        self.main_layout.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignRight)
        
        
    def add_bot_message(self, message):
        # Bot messages are styled with a light grey background, on the left
        # Using a div to control alignment and margin for the bubble
        html = f"""
        <div style="margin-bottom: 8px; text-align: left;">
            <p style="background-color: #e9ecef; color: #212529; 
                      display: inline-block; padding: 8px 12px; 
                      border-radius: 12px; border-bottom-left-radius: 2px; 
                      max-width: 75%; text-align: left;
                      margin-right: auto; margin-left: 0;">
                <b>Bot:</b> {message}
            </p>
        </div>
        """
        self.chat_display.append(html)
        self.chat_display.ensureCursorVisible() # Scroll to the bottom


    def add_user_message(self, message):
        # User messages are styled with a light blue/green background, on the right
        # Using a div to control alignment and margin for the bubble
        html = f"""
        <div style="margin-bottom: 8px; text-align: right;">
            <p style="background-color: #d1e7dd; color: #0f5132; 
                      display: inline-block; padding: 8px 12px; 
                      border-radius: 12px; border-bottom-right-radius: 2px;
                      max-width: 75%; text-align: left; /* Text inside bubble is left-aligned */
                      margin-left: auto; margin-right: 0;">
                <b>You:</b> {message}
            </p>
        </div>
        """
        self.chat_display.append(html)
        self.chat_display.ensureCursorVisible() # Scroll to the bottom


    def display_courses_for_selection(self, courses_data):
        self.courses = courses_data.get("courses", [])
        message = courses_data.get("message", "Could not retrieve courses.")

        if courses_data["status"] == "error":
            self.add_bot_message(f"Error: {message}")
            self.add_bot_message("Please check your token or network connection and try again.")
            # Potentially offer a way to go back or retry
            return

        if not self.courses:
            self.add_bot_message("No courses found or an error occurred.")
            return

        self.add_bot_message("Successfully fetched your courses!")
        self.add_bot_message("Please select a class you want to query:")

        # Clear previous buttons
        for i in reversed(range(self.input_area_layout.count())):
            widget = self.input_area_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for course in self.courses:
            btn = QPushButton(course["name"])
            btn.setFont(QFont("Arial", 11))
            btn.setMinimumHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #62967a; color: white; border-radius: 6px; padding: 8px;
                    border: none;
                }
                QPushButton:hover { background-color: #4BA173; }
                QPushButton:pressed { background-color: #188038; }
            """)
            # Use a lambda to pass the specific course when button is clicked
            btn.clicked.connect(lambda checked=False, c=course: self.on_course_button_selected(c))
            self.input_area_layout.addWidget(btn)
        self.input_area_layout.addStretch() # Push buttons to the top if not filling space
        
    
    def on_course_button_selected(self, course):
        self.add_user_message(f"Selected: {course['name']}")
        self.add_bot_message(f"Great! You selected '{course['name']}'. What would you like to ask about this course?")
        # Further interaction logic would go here.
        # For now, just emit a signal.
        self.course_selected.emit(course)

        # Clear course selection buttons after selection (optional)
        for i in reversed(range(self.input_area_layout.count())):
            item = self.input_area_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), QPushButton): # Only remove PushButtons
                 item.widget().deleteLater()
        self.input_area_layout.addStretch() # Ensure layout is still pushed up
        
    
    def handle_user_message(self):
        message = self.user_input.text().strip()
        if message:
            self.add_user_message(message)
            self.user_input.clear()
            # Optionally, add a bot response for demonstration
            self.add_bot_message("This is a bot reply placeholder.")



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Course Compass")
        self.setGeometry(100, 100, 800, 700)

        # Apply a basic style
        self.setStyleSheet("""
            QMainWindow { background-color: #f8f9fa; }
            QLabel { color: #212529; }
            QLineEdit { 
                border: 1px solid #ced4da; 
                border-radius: 4px; 
                padding: 6px 10px; 
                background-color: white; 
                font-size: 11pt;
            }
            QPushButton {
                background-color: #0d6efd; 
                color: white; 
                border: none;
                padding: 10px 15px; 
                border-radius: 6px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:pressed { background-color: #0a58ca; }
            /* QTextEdit styling is now handled in ChatbotScreen for chat_display */
            QScrollArea { border: none; }
        """)
        
        self.setWindowIcon(QIcon("resources/icon.png"))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create screens
        self.welcome_screen = WelcomeScreen()
        self.chatbot_screen = ChatbotScreen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.welcome_screen) # Index 0
        self.stacked_widget.addWidget(self.chatbot_screen) # Index 1
        
        # Connect signals
        self.welcome_screen.token_submitted.connect(self.handle_token_submission)
        self.chatbot_screen.back_button.clicked.connect(self.show_welcome_screen)
        self.chatbot_screen.course_selected.connect(self.handle_course_selection_for_query)
        
        self.show_welcome_screen()
        
        
    def show_welcome_screen(self):
        self.stacked_widget.setCurrentIndex(0)
        # Clear any previous status on welcome screen if going back
        self.welcome_screen.status_label.setText("")
        # Reload token into field if user goes back
        token = load_token()
        if token:
            self.welcome_screen.token_input.setText(token)
            
            
    def show_chatbot_screen(self):
        self.stacked_widget.setCurrentIndex(1)
        
        
    def handle_token_submission(self, token):
        # This is where you'd use the token to fetch courses
        print(f"Token submitted: {token[:5]}...") # Log for debugging
        courses_data = fetch_canvas_courses(token)

        self.show_chatbot_screen() # Switch to chatbot screen
        self.chatbot_screen.chat_display.clear() # Clear previous chat
        self.chatbot_screen.add_bot_message("Connecting to Canvas...")
        self.chatbot_screen.display_courses_for_selection(courses_data)


    def handle_course_selection_for_query(self, course):
        print(f"Course selected for query: {course['name']} (ID: {course['id']})")
        # Here you would implement the logic for what happens after a course is selected.
        # For example, you might enable a text input for the user to type their query
        # about the selected course.
        self.chatbot_screen.add_bot_message("You can now ask questions about this course (functionality to be implemented).")
        # Example: self.chatbot_screen.enable_query_input()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Basic theming for a slightly more modern look
    # app.setStyle("Fusion")
    with open("resources/styles.css", "r") as file:
        app.setStyleSheet(file.read())


    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())