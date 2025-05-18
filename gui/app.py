import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QStackedWidget,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor


class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Welcome to Canvas Course Query!")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Course Compass")

        # Apply a basic style
        self.setStyleSheet("""
            QMainWindow { background-color: #e9ecef; }
            QLabel { color: #343a40; }
            QLineEdit { border: 1px solid #ced4da; border-radius: 4px; padding: 6px; background-color: white; }
            QPushButton {
                background-color: #007bff; color: white; border: none;
                padding: 10px 15px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:pressed { background-color: #004085; }
            QTextEdit { border: 1px solid #ced4da; border-radius: 4px; background-color: white; }
        """)
        self.setWindowIcon(QIcon("resources/icon.png"))

        # # Main layout
        # self.central_widget = QWidget()
        # self.layout = QVBoxLayout(self.central_widget)

        # # Create six buttons for class options
        # self.buttons = []
        # for i in range(1, 7):
        #     button = QPushButton(f"Class {i}")
        #     button.clicked.connect(self.handle_button_click)
        #     self.layout.addWidget(button)
        #     self.buttons.append(button)

        # self.setCentralWidget(self.central_widget)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create screens
        self.welcome_screen = WelcomeScreen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.welcome_screen) # Index 0


    def handle_button_click(self):
        # Get the button that was clicked
        button = self.sender()
        if button:
            print(f"{button.text()} selected!")

            # Clear the layout
            for btn in self.buttons:
                self.layout.removeWidget(btn)
                btn.hide()

            # Add the clicked button to the top
            self.layout.addWidget(button)
            button.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Basic theming for a slightly more modern look
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240)) # Light grey window background
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255)) # White for input fields
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(230, 230, 230))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Button, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218)) # Blue highlight
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)


    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())