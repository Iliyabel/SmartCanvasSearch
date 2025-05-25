import sys
import json
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget,
    QScrollArea, QSizePolicy, QGraphicsDropShadowEffect, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QPainter


#=========================================================
class RoundedLabel(QLabel):
    """
    A custom QLabel that displays text with a rounded background.
    The label automatically adjusts its size to the text content.
    """
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        # --- Customizable Properties ---
        self._padding = 10  # Padding around the text, inside the rounded background
        self._border_radius = 15  # Radius of the rounded corners
        self._background_color = QColor(220, 220, 240, 200) # Default: Light grayish blue with some transparency
        self._text_color = QColor(Qt.GlobalColor.black) # Default: Black text color

        # Set contents margins. This is key to ensure text is not clipped.
        # The QLabel will render its text within these margins.
        self.setContentsMargins(self._padding, self._padding, self._padding, self._padding)
        
        # Set alignment if desired (e.g., center text within the label)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Set size policy:
        # Horizontal: Maximum - Prevents stretching beyond its preferred width (sizeHint).
        # Vertical: Preferred - Allows height to adjust, e.g., for word wrap.
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

    def setText(self, text):
        """
        Sets the text of the label and triggers a geometry update.
        """
        super().setText(text)
        # When text changes, the label's sizeHint might change.
        # updateGeometry() informs the layout system.
        self.updateGeometry() 
        self.adjustSize()

    def setPadding(self, padding: int):
        """
        Sets the padding around the text.
        """
        self._padding = padding
        self.setContentsMargins(self._padding, self._padding, self._padding, self._padding)
        self.updateGeometry() # Size hint might change due to margins
        self.update() # Trigger repaint

    def getPadding(self) -> int:
        return self._padding

    def setBorderRadius(self, radius: int):
        """
        Sets the border radius for the rounded background.
        """
        self._border_radius = radius
        self.update() # Trigger repaint

    def getBorderRadius(self) -> int:
        return self._border_radius

    def setBackgroundColor(self, color: QColor | str):
        """
        Sets the background color of the rounded rectangle.
        Accepts QColor object or a color name string.
        """
        if isinstance(color, str):
            self._background_color = QColor(color)
        elif isinstance(color, QColor):
            self._background_color = color
        else:
            # Fallback to default if invalid type
            self._background_color = QColor(220, 220, 240, 200) 
            print(f"Warning: Invalid color type for setBackgroundColor. Using default.")
        self.update() # Trigger repaint

    def getBackgroundColor(self) -> QColor:
        return self._background_color

    def setTextColor(self, color: QColor | str):
        """
        Sets the text color.
        """
        if isinstance(color, str):
            self._text_color = QColor(color)
        elif isinstance(color, QColor):
            self._text_color = color
        else:
            self._text_color = QColor(Qt.GlobalColor.black)
            print(f"Warning: Invalid color type for setTextColor. Using default.")
        
        # Update stylesheet for text color - QLabel handles this efficiently
        self.setStyleSheet(f"color: {self._text_color.name()};")
        # No need to call self.update() here as setStyleSheet implies an update.

    def paintEvent(self, event):
        """
        Overrides the paint event to draw the rounded background
        before drawing the text.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set brush and pen for the background
        painter.setBrush(self._background_color)
        painter.setPen(Qt.PenStyle.NoPen) # No border outline for the rounded rect itself

        # Draw the rounded rectangle. self.rect() is the entire widget area.
        painter.drawRoundedRect(self.rect(), self._border_radius, self._border_radius)

        # Let the base QLabel class draw the text.
        # It will draw the text within the contentsMargins we've set.
        super().paintEvent(event)





#==========================================================

class CourseSelectionScreen(QWidget):
    course_selected = pyqtSignal(dict)  # Signal to send the selected course

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(50, 20, 50, 20)
        self.main_layout.setSpacing(10)

        # Title
        title_label = QLabel("Select a Course")
        title_label.setObjectName("course_selection_title")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)

        # Placeholder for course buttons
        self.course_buttons_layout = QVBoxLayout()
        self.course_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addLayout(self.course_buttons_layout)

        # Load courses (temporary data for now)
        self.load_courses()

    def load_courses(self):
        # Temporary data (replace with file-based fetching later)
        courses = [
            {"id": 1, "name": "Course 1"},
            {"id": 2, "name": "Course 2 hhhh wewew awdas"},
            {"id": 3, "name": "Course 3"},
        ]

        # Create a button for each course
        for course in courses:
            button = QPushButton(course["name"])
            button.setObjectName("course_button")
            shadow = QGraphicsDropShadowEffect(blurRadius=4, xOffset=0, yOffset=2)
            button.setGraphicsEffect(shadow)
            button.clicked.connect(lambda _, c=course: self.select_course(c))
            self.course_buttons_layout.addWidget(button)
            
            self.course_buttons_layout.setAlignment(button, Qt.AlignmentFlag.AlignCenter)

    def select_course(self, course):
        self.course_selected.emit(course)  # Emit the selected course


class ChatbotScreen(QWidget):
    course_selected = pyqtSignal(dict)
    shadow = QGraphicsDropShadowEffect(blurRadius=4, xOffset=0, yOffset=2)

    def __init__(self):
        super().__init__()
        self.selected_course = None  # Store the selected course
        self.courses = []
        self.chat_history = []  # List of (sender, message) tuples
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(50, 20, 50, 20)
        self.main_layout.setSpacing(10)

        # Selected course label
        self.selected_course_label = QLabel("No course selected")
        self.selected_course_label.setObjectName("selected_course_label")
        self.selected_course_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_course_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred) 
        self.main_layout.addWidget(self.selected_course_label, 0, Qt.AlignmentFlag.AlignLeft)

        # Scroll area for chat bubbles
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_container.setObjectName("chat_container")
        
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(5)
        self.scroll_area.setWidget(self.chat_container)
        self.main_layout.addWidget(self.scroll_area, 1)

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
        self.run_button.setGraphicsEffect(self.shadow)
        
        self.run_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.run_button.clicked.connect(self.handle_user_message)
        self.bottom_input_layout.addWidget(self.run_button)

        self.main_layout.addWidget(self.bottom_input_widget, 0, Qt.AlignmentFlag.AlignBottom)

        # Back to Welcome Screen button
        self.back_button = QPushButton("Back to Token Setup")
        self.back_button.setObjectName("back_button")
        
        self.back_button.setFont(QFont("Arial", 10))
        self.main_layout.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignRight)
        
        
    def set_selected_course(self, course):
        self.selected_course = course
        self.selected_course_label.setText(f"Selected Course: {course['name']}")


    def add_message(self, sender, message):
        self.chat_history.append((sender, message))

        max_bubble_width = 1000  #px

        row_widget = QWidget()
        row_widget.setStyleSheet("border: 3px solid blue;") # FOR DEBUGGING
        row_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5) # Spacing between messages

        if sender == "user":

            # User declaration label
            title_label = QLabel()
            title_label.setObjectName("user_title")
            title_label.setText("You")
            row_layout.addWidget(title_label, 0, Qt.AlignmentFlag.AlignRight)
            
            # Message label
            label = QLabel()
            label.setObjectName("user_message")
            label.setWordWrap(True)
            # label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            # label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setText(message)
            # label.setMaximumWidth(max_bubble_width) 
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            label.setTextFormat(Qt.TextFormat.RichText)

            
            
            # label = RoundedLabel(message)
            # label.setObjectName("user_message")
            # label.setBackgroundColor("#C3E1A9")
            # label.maximumWidth = max_bubble_width
            # label.setWordWrap(True)
            # label.setTextColor("#0f5132")
            # label.setBorderRadius(10)
            # label.setPadding(8)
            # label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            # label.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            
            
            # row_widget.updateGeometry()
            row_layout.addWidget(label, 1, Qt.AlignmentFlag.AlignRight)
            self.chat_layout.addWidget(row_widget, 0, Qt.AlignmentFlag.AlignTop)
            
        else:
            # Bot message: left-aligned with icon

            # Icon label
            icon_label = QLabel()
            icon_label.setFixedSize(50, 50)
            icon_label.setScaledContents(True)
            icon_label.setPixmap(QIcon("resources/icon.png").pixmap(50, 50))
            row_layout.addWidget(icon_label, 0, alignment=Qt.AlignmentFlag.AlignTop)

            # Message label
            msg_label = QLabel()
            msg_label.setObjectName("bot_message")
            msg_label.setWordWrap(True)
            msg_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            # msg_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            msg_label.setText(message)
            msg_label.setMaximumWidth(max_bubble_width)
            msg_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
            
            
            # msg_label = RoundedLabel(message)
            # msg_label.setObjectName("user_message")
            # msg_label.setBackgroundColor("#95c8ad")
            # msg_label.setWordWrap(True)
            # msg_label.setTextColor("#212529")
            # msg_label.setBorderRadius(10)
            # msg_label.setPadding(8)
            
            


            row_layout.addWidget(msg_label, 1, Qt.AlignmentFlag.AlignLeft)

            self.chat_layout.addWidget(row_widget, 0, Qt.AlignmentFlag.AlignTop)

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
        self.course_selection_screen = CourseSelectionScreen()
        self.chatbot_screen = ChatbotScreen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.course_selection_screen)  # Index 0
        self.stacked_widget.addWidget(self.chatbot_screen)           # Index 1
        
        # Connect signals
        self.course_selection_screen.course_selected.connect(self.handle_course_selection)
        
        self.show_course_selection_screen()
        
    def show_course_selection_screen(self):
        self.stacked_widget.setCurrentIndex(0)
            
    def show_chatbot_screen(self):
        self.stacked_widget.setCurrentIndex(1)
        

    def handle_course_selection(self, course):
        # Pass the selected course to the chatbot screen
        self.chatbot_screen.set_selected_course(course)
        self.show_chatbot_screen()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    with open("resources/styles.css", "r") as file:
        app.setStyleSheet(file.read())

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())