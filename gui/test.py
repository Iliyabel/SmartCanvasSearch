import sys
import json
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QStackedWidget,
    QScrollArea, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor



class ChatbotScreen(QWidget):
    course_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.courses = []
        self.chat_history = []  # List of (sender, message) tuples
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(50, 20, 50, 20)
        self.main_layout.setSpacing(10)

        # Scroll area for chat bubbles
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_container.setObjectName("chat_container")
        
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.chat_container)
        self.main_layout.addWidget(self.scroll_area, 1)

        # Spacer to push input area to the bottom
        self.main_layout.addStretch()

        # --- Input area at the bottom ---
        self.bottom_input_widget = QWidget()
        self.bottom_input_widget.setObjectName("bottom_input_widget")
        self.bottom_input_layout = QHBoxLayout(self.bottom_input_widget)
        self.bottom_input_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_input_layout.setSpacing(8)

        self.user_input = QLineEdit()
        self.user_input.setObjectName("user_input")
        self.user_input.setPlaceholderText("Enter a question...")
        self.bottom_input_layout.addWidget(self.user_input, 1)

        self.run_button = QPushButton("Run")
        self.run_button.setObjectName("run_button")
        self.run_button.setMinimumWidth(80)
        
        self.run_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.run_button.clicked.connect(self.handle_user_message)
        self.bottom_input_layout.addWidget(self.run_button)

        self.main_layout.addWidget(self.bottom_input_widget, 0, Qt.AlignmentFlag.AlignBottom)

        # Back to Welcome Screen button
        self.back_button = QPushButton("Back to Token Setup")
        self.back_button.setObjectName("back_button")
        
        self.back_button.setFont(QFont("Arial", 10))
        self.main_layout.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignRight)


    def add_message(self, sender, message):
        self.chat_history.append((sender, message))

        max_bubble_width = 400  #px

        row_widget = QWidget()
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5) # Spacing between messages

        if sender == "user":
            # User message: right-aligned

            # User declaration label
            title_label = QLabel()
            title_label.setObjectName("user_title")
            title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            title_label.setText("You")
            row_layout.addWidget(title_label)
            
            # Message label
            label = QLabel()
            label.setObjectName("user_message")
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setText(f"{message}")
            label.setMaximumWidth(max_bubble_width)
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
            row_layout.addWidget(label)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

            self.chat_layout.addWidget(row_widget)
        else:
            # Bot message: left-aligned with icon

            # Icon label
            icon_label = QLabel()
            icon_label.setFixedSize(50, 50)
            icon_label.setScaledContents(True)
            icon_label.setPixmap(QIcon("resources/icon.png").pixmap(50, 50))
            row_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignLeft)

            # Message label
            msg_label = QLabel()
            msg_label.setObjectName("bot_message")
            msg_label.setWordWrap(True)
            msg_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg_label.setText(message)
            msg_label.setMaximumWidth(max_bubble_width)
            msg_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

            row_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)
            row_layout.addWidget(msg_label, 1, Qt.AlignmentFlag.AlignTop)
            # row_layout.addStretch()  # Pushes the message to the left
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.chat_layout.addWidget(row_widget)

        QApplication.processEvents()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def add_user_message(self, message):
        self.add_message("user", message)

    def add_bot_message(self, message):
        self.add_message("bot", message)

    def handle_user_message(self):
        message = self.user_input.text().strip()
        if message:
            self.add_user_message(message)
            self.user_input.clear()
            # Optionally, add a bot response for demonstration
            self.add_bot_message("This is a bot reply placeholder.")

    def on_course_button_selected(self, course):
        self.add_user_message(f"Selected: {course['name']}")
        self.add_bot_message(f"Great! You selected '{course['name']}'. What would you like to ask about this course?")
        self.course_selected.emit(course)
        for i in reversed(range(self.input_area_layout.count())):
            item = self.input_area_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), QPushButton):
                item.widget().deleteLater()
        self.input_area_layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Course Compass")
        self.setGeometry(500, 100, 1000, 800)
        
        self.setWindowIcon(QIcon("resources/icon.png"))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create screens
        self.chatbot_screen = ChatbotScreen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.chatbot_screen) # Index 0
        
        # Connect signals
        self.chatbot_screen.course_selected.connect(self.handle_course_selection_for_query)
        
        self.show_chatbot_screen()
        
            
    def show_chatbot_screen(self):
        self.stacked_widget.setCurrentIndex(1)
        

    def handle_course_selection_for_query(self, course):
        print(f"Course selected for query: {course['name']} (ID: {course['id']})")
        # Here you would implement the logic for what happens after a course is selected.
        # For example, you might enable a text input for the user to type their query
        # about the selected course.
        self.chatbot_screen.add_bot_message("You can now ask questions about this course (functionality to be implemented).")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Basic theming for a slightly more modern look
    # app.setStyle("Fusion")

    with open("resources/styles.css", "r") as file:
        app.setStyleSheet(file.read())

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())