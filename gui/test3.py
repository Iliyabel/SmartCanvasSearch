import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, 
    QGraphicsDropShadowEffect, QStackedWidget, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class CourseSelectionScreen(QWidget):
    course_selected = pyqtSignal(str) # Signal to emit when a course is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(50, 20, 50, 20)

        title_label = QLabel("Select a Course")
        title_label.setObjectName("course_selection_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)

        # Grid for course buttons for better arrangement
        self.buttons_layout = QGridLayout()
        self.buttons_layout.setSpacing(15)

        # Example courses - you can populate this dynamically
        courses = [
            "Introduction to Python", "Web Development Basics",
            "Data Structures & Algorithms", "Machine Learning Fundamentals",
            "Advanced Calculus", "Organic Chemistry"
        ]

        row, col = 0, 0
        for course_name in courses:
            button = QPushButton(course_name)
            button.setObjectName("course_button")
            shadow = QGraphicsDropShadowEffect(blurRadius=4, xOffset=0, yOffset=2)
            button.setGraphicsEffect(shadow)
            button.setMinimumHeight(50)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda checked=False, name=course_name: self.course_button_clicked(name))
            self.buttons_layout.addWidget(button, row, col)
            col += 1
            if col >= 2: # Adjust number of columns as needed (e.g., 2 columns)
                col = 0
                row += 1
        
        self.layout.addLayout(self.buttons_layout)
        self.layout.addStretch(1) # Add stretch to push buttons up if few

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
        self.main_layout.setContentsMargins(50, 20, 50, 20) # Chat screen takes full space
        self.main_layout.setSpacing(10)

        self.selected_course_label = QLabel("No course selected")
        self.selected_course_label.setObjectName("selected_course_label")
        self.selected_course_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.selected_course_label, 0, Qt.AlignmentFlag.AlignLeft)

        # Define shadow effect for the run button
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(Qt.GlobalColor.darkGray)
        self.shadow.setOffset(2, 2)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.chat_container_widget = QWidget()
        self.chat_container_widget.setObjectName("chat_container_widget")
        
        self.chat_layout = QVBoxLayout(self.chat_container_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(8)

        self.scroll_area.setWidget(self.chat_container_widget)
        self.main_layout.addWidget(self.scroll_area, 1)

        self.bottom_input_widget = QWidget()
        self.bottom_input_widget.setObjectName("bottom_input_widget")
        self.bottom_input_layout = QHBoxLayout(self.bottom_input_widget)
        self.bottom_input_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_input_layout.setSpacing(8)

        self.user_input = QLineEdit()
        self.user_input.setObjectName("user_input")
        self.user_input.setPlaceholderText("Enter a question...")
        self.user_input.setFont(QFont("Arial", 10))
        self.user_input.returnPressed.connect(self.handle_user_message)
        self.bottom_input_layout.addWidget(self.user_input, 1)

        self.run_button = QPushButton("Run")
        self.run_button.setObjectName("run_button")
        self.run_button.setGraphicsEffect(self.shadow)
        self.run_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.run_button.clicked.connect(self.handle_user_message)
        self.bottom_input_layout.addWidget(self.run_button)

        self.main_layout.addWidget(self.bottom_input_widget, 0, Qt.AlignmentFlag.AlignBottom)

    def set_selected_course(self, course_name):
        self.selected_course_label.setText(course_name)
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
        self.setGeometry(500, 100, 1000, 800)
        self.setWindowIcon(QIcon("resources/icon.png"))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.course_selection_screen = CourseSelectionScreen()
        self.chat_screen = ChatScreenWidget()

        self.stacked_widget.addWidget(self.course_selection_screen) # Index 0
        self.stacked_widget.addWidget(self.chat_screen)           # Index 1

        # Connect signals
        self.course_selection_screen.course_selected.connect(self.handle_course_selection)
        
        self.show_course_selection_screen() # Start with course selection

    def show_course_selection_screen(self):
        self.stacked_widget.setCurrentIndex(0)
            
    def show_chat_screen(self):
        self.stacked_widget.setCurrentIndex(1)
        
    def handle_course_selection(self, course_name):
        self.chat_screen.set_selected_course(course_name)
        self.show_chat_screen()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    try:
        with open("resources/styles2.css", "r") as file: # Ensure this CSS file exists
            app.setStyleSheet(file.read())
    except FileNotFoundError:
        print("Warning: resources/styles2.css not found. Using default styles.")
    
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())