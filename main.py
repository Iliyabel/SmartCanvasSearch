import sys
import os

# --- Add project root to sys.path ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from PyQt6.QtWidgets import QApplication
from gui.app import MainWindow


def run_application():
    """
    Initializes and runs the PyQt6 application.
    """
    app = QApplication(sys.argv)

    # --- Load Stylesheet ---
    stylesheet_path = os.path.join(PROJECT_ROOT, "resources", "styles.css")
    try:
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, "r") as file:
                app.setStyleSheet(file.read())
            print(f"Stylesheet loaded from: {stylesheet_path}")
        else:
            print(f"Warning: Stylesheet not found at {stylesheet_path}. Using default styles.")
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
    # --- End Stylesheet Loading ---

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"System Path includes: {PROJECT_ROOT in sys.path}")
    print("Starting Course Compass application...")
    run_application()