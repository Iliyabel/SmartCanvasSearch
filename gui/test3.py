import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon

class ChatMessageWidget(QWidget):
    """
    A widget to display a single chat message with a sender title and the message content.
    """
    def __init__(self, sender_name, message_text, is_user_message):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 2, 5, 2) # Reduced margins for tighter packing
        self.layout.setSpacing(2) # Spacing between title and message

        self.sender_label = QLabel(sender_name)
        self.sender_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        self.message_label = QLabel(message_text)
        self.message_label.setWordWrap(True)
        # self.message_label.setFont(QFont("Arial", 14))
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Basic styling for bubbles
        bubble_style_sheet = """
            QLabel {{
                padding: 8px;
                border-radius: 12px;
                background-color: {background_color};
                color: {text_color};
            }}
        """
        
        if is_user_message:
            self.sender_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.sender_label.setObjectName("user_title")
            self.message_label.setObjectName("user_message")
            self.message_label.setStyleSheet(bubble_style_sheet.format(background_color="#C3E1A9", text_color="#0f5132"))
            self.layout.addWidget(self.sender_label, alignment=Qt.AlignmentFlag.AlignRight)
            self.layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            self.sender_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.message_label.setObjectName("bot_message")
            self.message_label.setStyleSheet(bubble_style_sheet.format(background_color="#95c8ad", text_color="#212529"))
            self.layout.addWidget(self.sender_label, alignment=Qt.AlignmentFlag.AlignLeft)
            self.layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Ensure the message label can expand vertically
        self.message_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Course Compass")
        self.setGeometry(500, 100, 1000, 800)
        
        self.setWindowIcon(QIcon("resources/icon.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(50, 20, 50, 20)
        self.main_layout.setSpacing(10)

        # Define shadow effect for the run button
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(Qt.GlobalColor.darkGray)
        self.shadow.setOffset(2, 2)

        # Scroll area for chat messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_container_widget = QWidget() # This widget will hold the chat_layout
        self.chat_container_widget.setObjectName("chat_container_widget")
        
        self.chat_layout = QVBoxLayout(self.chat_container_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Messages stack from the top
        self.chat_layout.setSpacing(8) # Spacing between message bubbles

        self.scroll_area.setWidget(self.chat_container_widget)
        self.main_layout.addWidget(self.scroll_area, 1) # Scroll area takes most space

        # --- Input area at the bottom ---
        self.bottom_input_widget = QWidget()
        self.bottom_input_widget.setObjectName("bottom_input_widget")
        self.bottom_input_layout = QHBoxLayout(self.bottom_input_widget)
        self.bottom_input_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_input_layout.setSpacing(8)

        self.user_input = QLineEdit()
        self.user_input.setObjectName("user_input")
        self.user_input.setPlaceholderText("Enter a question...")
        self.user_input.setFont(QFont("Arial", 10)) 
        self.user_input.returnPressed.connect(self.send_message) # Send on Enter
        self.bottom_input_layout.addWidget(self.user_input, 1)

        self.run_button = QPushButton("Run")
        self.run_button.setObjectName("run_button")
        self.run_button.setGraphicsEffect(self.shadow)
        
        self.run_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.run_button.clicked.connect(self.send_message)
        self.bottom_input_layout.addWidget(self.run_button)

        self.main_layout.addWidget(self.bottom_input_widget, 0, Qt.AlignmentFlag.AlignBottom)


        self.add_automated_message("Welcome to the Course Compass!")
        self.add_automated_message("Please ask a question about your course materials.")


    def add_message_to_chat(self, sender_name, message_text, is_user):
        if not message_text.strip():
            return

        message_widget = ChatMessageWidget(sender_name, message_text, is_user)
        
        # Create a container widget for alignment within the chat_layout
        # This helps ensure user messages are pushed to the right and bot to the left
        # if the chat_layout itself is wider than the messages.
        alignment_container = QWidget()
        alignment_layout = QHBoxLayout(alignment_container)
        alignment_layout.setContentsMargins(0,0,0,0)

        if is_user:
            alignment_layout.addStretch(1) # Push to the right
            # AlignTop makes sure message does not stretch vertically
            alignment_layout.addWidget(message_widget, alignment=Qt.AlignmentFlag.AlignTop)
        else:
            alignment_layout.addWidget(message_widget, alignment=Qt.AlignmentFlag.AlignTop)
            alignment_layout.addStretch(1) # Push to the left (content already left-aligned)
        
        self.chat_layout.addWidget(alignment_container)

        # Ensure the scroll area scrolls to the bottom
        # Use QTimer to allow the layout to update before scrolling
        QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def send_message(self):
        user_text = self.user_input.text()
        self.add_message_to_chat("You", user_text, True)
        self.user_input.clear()

    def add_automated_message(self, custom_message=None):
        messages = [
            "Hello there!", "How are you doing today?", "This is an automated message.",
            "PyQt6 is quite versatile.", "Keep coding!", "Have a great day!"
        ]
        import random
        message = custom_message if custom_message else random.choice(messages)
        self.add_message_to_chat("Bot", message, False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    with open("resources/styles2.css", "r") as file:
        app.setStyleSheet(file.read())
    
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())