import sys
import os

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Now import and run the main GUI application
from main_gui import MainAppGUI, QApplication

if __name__ == "__main__":
    # You could add platform env settings here if needed globally
    # os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = QApplication(sys.argv)
    gui = MainAppGUI()
    gui.show()
    sys.exit(app.exec()) 