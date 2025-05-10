import sys

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Course Selector")
        self.setFixedSize(QSize(400, 300))

        # Main layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Create six buttons for class options
        self.buttons = []
        for i in range(1, 7):
            button = QPushButton(f"Class {i}")
            button.clicked.connect(self.handle_button_click)
            self.layout.addWidget(button)
            self.buttons.append(button)

        self.setCentralWidget(self.central_widget)

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


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()