import sys
import os
import time
import cv2
import numpy as np
from face_operations import detector as face_detector
from face_operations import training as face_trainer
from system_actions import host_blocker as block_websites
from system_actions import email_notifier as emailalert
from system_actions import browser_extension as browser_ext
from system_actions import block_service as block_service
from dataset_creator_gui import DatasetCreatorDialog
from password_dialog import PasswordDialog
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QDialog,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox, QSizePolicy, QStackedWidget,
    QFrame, QCheckBox, QGroupBox, QListWidget, QListWidgetItem, QComboBox
)
from PyQt6.QtGui import QFont, QColor, QPalette, QImage, QPixmap, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QSize, QSettings

# Define base path relative to this script's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- Stylesheets ---
LIGHT_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f8f9fa;
    color: #212529;
    font-family: "Segoe UI", Arial, sans-serif;
}
QWidget#sidebar {
    background-color: #e9ecef;
}
QPushButton#navButton {
    background-color: transparent;
    border: none;
    color: #495057;
    padding: 10px;
    text-align: left;
    font-size: 11pt;
    border-radius: 5px;
}
QPushButton#navButton:hover {
    background-color: #dee2e6;
}
QPushButton#navButton:checked {
    background-color: #0d6efd;
    color: white;
    font-weight: bold;
}
QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    padding: 8px 15px;
    font-size: 10pt;
    border-radius: 5px;
    min-width: 100px;
}
QPushButton:hover {
    background-color: #0b5ed7;
}
QPushButton:pressed {
    background-color: #0a58ca;
}
QPushButton:disabled {
    background-color: #6c757d;
    color: #e9ecef;
}
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    color: #212529;
    font-family: "Courier New", monospace;
    border-radius: 5px;
    padding: 5px;
}
QLabel {
    border: none;
    font-size: 10pt;
}
QLabel#statusLabel {
    font-size: 16pt;
    font-weight: bold;
    padding: 10px;
}
QLabel#webcamLabel {
    border: 1px solid #dee2e6;
    background-color: #ffffff;
    border-radius: 5px;
}
QLabel#titleLabel {
    font-size: 14pt;
    font-weight: bold;
    color: #0d6efd;
    padding-bottom: 10px;
    border-bottom: 1px solid #dee2e6;
}
QFrame#separator {
    background-color: #dee2e6;
}
QListWidget {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 5px;
    padding: 5px;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #f0f0f0;
}
QListWidget::item:selected {
    background-color: #e9ecef;
    color: #212529;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
}
QComboBox {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 5px;
    padding: 5px;
    min-width: 100px;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    selection-background-color: #e9ecef;
    selection-color: #212529;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    margin-top: 1ex;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QMenuBar {
    background-color: #f8f9fa;
}
QMenuBar::item {
    spacing: 5px;
    padding: 5px 10px;
}
QMenuBar::item:selected {
    background: #e9ecef;
}
QMenu {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
}
QMenu::item {
    padding: 6px 20px;
}
QMenu::item:selected {
    background-color: #e9ecef;
}
"""

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #121212;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
}
QWidget#sidebar {
    background-color: #1e1e1e;
}
QPushButton#navButton {
    background-color: transparent;
    border: none;
    color: #b0b0b0;
    padding: 10px;
    text-align: left;
    font-size: 11pt;
    border-radius: 5px;
}
QPushButton#navButton:hover {
    background-color: #2d2d2d;
}
QPushButton#navButton:checked {
    background-color: #1976d2;
    color: white;
    font-weight: bold;
}
QPushButton {
    background-color: #1976d2;
    color: white;
    border: none;
    padding: 8px 15px;
    font-size: 10pt;
    border-radius: 5px;
    min-width: 100px;
}
QPushButton:hover {
    background-color: #1565c0;
}
QPushButton:pressed {
    background-color: #0d47a1;
}
QPushButton:disabled {
    background-color: #5c5c5c;
    color: #2d2d2d;
}
QTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #3e3e3e;
    color: #e0e0e0;
    font-family: "Courier New", monospace;
    border-radius: 5px;
    padding: 5px;
}
QLabel {
    border: none;
    font-size: 10pt;
}
QLabel#statusLabel {
    font-size: 16pt;
    font-weight: bold;
    padding: 10px;
}
QLabel#webcamLabel {
    border: 1px solid #3e3e3e;
    background-color: #1e1e1e;
    border-radius: 5px;
}
QLabel#titleLabel {
    font-size: 14pt;
    font-weight: bold;
    color: #2196f3;
    padding-bottom: 10px;
    border-bottom: 1px solid #3e3e3e;
}
QFrame#separator {
    background-color: #3e3e3e;
}
QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    padding: 5px;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #2d2d2d;
}
QListWidget::item:selected {
    background-color: #2d2d2d;
    color: #e0e0e0;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
}
QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    padding: 5px;
    color: #e0e0e0;
    min-width: 100px;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    border: 1px solid #3e3e3e;
    selection-background-color: #2d2d2d;
    selection-color: #e0e0e0;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    margin-top: 1ex;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QMenuBar {
    background-color: #1e1e1e;
}
QMenuBar::item {
    spacing: 5px;
    padding: 5px 10px;
}
QMenuBar::item:selected {
    background: #2d2d2d;
}
QMenu {
    background-color: #1e1e1e;
    border: 1px solid #3e3e3e;
}
QMenu::item {
    padding: 6px 20px;
}
QMenu::item:selected {
    background-color: #2d2d2d;
}
QMenu::separator {
    height: 1px;
    background-color: #3e3e3e;
    margin: 5px 10px;
}
"""

# Worker thread for running detection/actions without freezing GUI
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    result = pyqtSignal(bool, int, str, str)
    frame_update = pyqtSignal(QImage) # Signal to send video frames

    def run(self):
        self.progress.emit("Worker thread started. Loading models...")
        if not face_detector.load_models(models_dir=MODELS_DIR):
            self.progress.emit("❌ Error: Failed to load required models. Aborting.")
            self.result.emit(False, -1, "Model load failed", "Model load failed")
            self.finished.emit()
            return
        self.progress.emit("✅ Models loaded successfully.")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.progress.emit("❌ Error: Cannot open webcam.")
            self.result.emit(False, -1, "Webcam error", "Webcam error")
            self.finished.emit()
            return
        self.progress.emit("📷 Webcam opened.")

        start_time = time.time()
        duration_seconds = 10
        age_predictions = []
        content_restricted = False
        final_stable_age = -1

        self.progress.emit(f"🔹 Running face analysis for {duration_seconds} seconds...")

        while time.time() - start_time < duration_seconds:
            ret, frame = cap.read()
            if not ret:
                self.progress.emit("Warning: Cannot read frame from webcam.")
                time.sleep(0.1)
                continue

            display_frame = frame.copy() # Draw on this copy
            name, face_coords = face_detector.predict_face(frame)
            stable_age = -1

            if face_coords:
                (x, y, w, h) = face_coords
                # Draw rectangle for detected face
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                if name not in ["No face", "Error", "Unknown"]:
                    predicted_age = face_detector.predict_age(frame, face_coords)
                    if predicted_age != -1:
                        age_predictions.append(predicted_age)
                        if len(age_predictions) > 5:
                            age_predictions.pop(0)
                        if age_predictions:
                            stable_age = int(np.mean(age_predictions))
                            final_stable_age = stable_age

                        # Draw name and age on frame
                        age_text = f" Age: {stable_age}" if stable_age != -1 else ""
                        info_text = f"{name}{age_text}"
                        cv2.putText(display_frame, info_text, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                        # Check restriction
                        if stable_age != -1 and stable_age < 18:
                            content_restricted = True # Latch if child detected once
                elif name != "No face":
                    # Still draw name if known but age failed or unknown name
                    cv2.putText(display_frame, name, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Emit the processed frame for GUI update
            try:
                rgb_image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.frame_update.emit(qt_image)
            except Exception as e:
                 self.progress.emit(f"Warning: Error converting/emitting frame: {e}")

            # Small delay to allow GUI updates and prevent busy-looping 100% CPU
            time.sleep(0.01) # Approx 100 FPS theoretical max, adjust if needed

        # --- Loop Finished --- 
        cap.release()
        self.progress.emit("✅ Analysis complete.")

        block_status = "No action needed."
        email_status = "No action needed."

        if content_restricted:
            self.progress.emit(f"🔴 Child detected (Final Age: {final_stable_age})! Blocking websites...")
            try:
                block_msg = block_websites.block_sites()
                block_status = block_msg if block_msg else "Blocking attempted."
                self.progress.emit(f"Block Status: {block_status}")
            except Exception as e:
                block_status = f"Error during blocking: {e}"
                self.progress.emit(f"Block Status: {block_status}")

            self.progress.emit("🔴 Sending email alert...")
            try:
                email_msg = emailalert.send_email_alert()
                email_status = email_msg if email_msg else "Email sending attempted."
                self.progress.emit(f"Email Status: {email_status}")
            except Exception as e:
                email_status = f"Error sending email: {e}"
                self.progress.emit(f"Email Status: {email_status}")
        else:
             if final_stable_age != -1:
                self.progress.emit(f"✅ No child detected (Final Age: {final_stable_age}).")
             else:
                 self.progress.emit("✅ No child detected or age detection failed.")

        self.result.emit(content_restricted, final_stable_age, block_status, email_status)
        self.finished.emit()

# Training Worker
class TrainWorker(QObject):
    finished = pyqtSignal(bool, str) # bool success, str message
    progress = pyqtSignal(str)

    def run(self):
        self.progress.emit("Starting face recognition training...")
        try:
            # Assuming train_model prints status but doesn't return specific message
            # We might need to modify train_model to return status later if needed
            face_trainer.train_model()
            self.progress.emit("✅ Training finished successfully.")
            self.finished.emit(True, "Training completed successfully.")
        except Exception as e:
            error_msg = f"❌ Error during training: {e}"
            self.progress.emit(error_msg)
            self.finished.emit(False, error_msg)

# Main Application Window
class MainAppGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.is_training = False
        self.monitor_thread = None
        self.monitor_worker = None
        self.train_thread = None
        self.train_worker = None
        
        # Load settings
        self.settings = QSettings("AI-Child-Protection", "MainApp")
        self.current_theme = self.settings.value("theme", "light")
        
        self.init_ui()
        self.apply_theme()
        self.check_initial_files() # Check files on startup

    def init_ui(self):
        self.setWindowTitle("AI Child Protection")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create menubar
        self.create_menubar()

        # --- Main Layout --- 
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_hbox = QHBoxLayout(main_widget)
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)

        # --- Sidebar --- 
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        # --- Content Area (Stacked Widget) --- 
        self.stacked_widget = QStackedWidget()

        # --- Sidebar Buttons --- 
        self.monitor_button = QPushButton("👁️ Monitor")
        self.monitor_button.setObjectName("navButton")
        self.monitor_button.setCheckable(True)
        self.monitor_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        self.blocking_button = QPushButton("🔒 Website Blocking")
        self.blocking_button.setObjectName("navButton")
        self.blocking_button.setCheckable(True)
        self.blocking_button.clicked.connect(self.open_blocking_tab)

        self.manage_button = QPushButton("👤 Manage Faces")
        self.manage_button.setObjectName("navButton")
        self.manage_button.setCheckable(True)
        self.manage_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        # Theme switcher
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark"])
        self.theme_selector.setCurrentIndex(0 if self.current_theme == "light" else 1)
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_selector)

        sidebar_layout.addWidget(QLabel("Navigation")) # Simple title for sidebar
        sidebar_layout.addWidget(self.monitor_button)
        sidebar_layout.addWidget(self.blocking_button)
        sidebar_layout.addWidget(self.manage_button)
        sidebar_layout.addStretch()
        sidebar_layout.addLayout(theme_layout)

        # --- Create Pages --- 
        self.monitor_page = self.create_monitor_page()
        self.blocking_page = self.create_blocking_page()
        self.manage_page = self.create_manage_page()

        self.stacked_widget.addWidget(self.monitor_page)
        self.stacked_widget.addWidget(self.blocking_page)
        self.stacked_widget.addWidget(self.manage_page)

        # --- Assemble Main Layout --- 
        main_hbox.addWidget(sidebar)
        main_hbox.addWidget(self.stacked_widget)

        # Set initial state
        self.monitor_button.setChecked(True)
        self.stacked_widget.setCurrentIndex(0)

    def create_menubar(self):
        """Create the application menubar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        # Theme submenu
        theme_menu = settings_menu.addMenu("Theme")
        
        # Light theme action
        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self.change_theme("Light"))
        theme_menu.addAction(light_action)
        
        # Dark theme action
        dark_action = QAction("Dark", self)
        dark_action.triggered.connect(lambda: self.change_theme("Dark"))
        theme_menu.addAction(dark_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def apply_theme(self):
        """Apply the current theme to the application."""
        if self.current_theme == "light":
            self.setStyleSheet(LIGHT_STYLESHEET)
        else:
            self.setStyleSheet(DARK_STYLESHEET)

    def change_theme(self, theme_name):
        """Change the application theme."""
        self.current_theme = theme_name.lower()
        self.settings.setValue("theme", self.current_theme)
        self.apply_theme()
        
        # Update combo box if called from menu
        if isinstance(theme_name, str):
            self.theme_selector.setCurrentText(theme_name)

    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About AI Child Protection",
            "<h2>AI Child Protection</h2>"
            "<p>Version 1.0</p>"
            "<p>This application uses face recognition and age estimation to detect if a child is using the computer, "
            "then blocks predefined websites to ensure a safe browsing experience.</p>"
            "<p>© 2025 Shristi Pandey</p>"
        )

    # --- Page Creation Methods --- 
    def create_monitor_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Webcam Area (Left)
        webcam_layout = QVBoxLayout()
        self.monitor_webcam_label = QLabel("Press 'Start Monitoring'")
        self.monitor_webcam_label.setObjectName("webcamLabel")
        self.monitor_webcam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monitor_webcam_label.setMinimumSize(640, 480)
        self.monitor_webcam_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        webcam_layout.addWidget(self.monitor_webcam_label)

        # Controls/Log Area (Right)
        controls_log_layout = QVBoxLayout()
        self.monitor_status_label = QLabel("Status: Idle")
        self.monitor_status_label.setObjectName("statusLabel")
        self.monitor_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_status_color(self.monitor_status_label, "idle") # Use helper for color

        self.start_monitor_button = QPushButton("Start Monitoring")
        self.start_monitor_button.clicked.connect(self.run_monitor_detection)

        self.monitor_log_output = QTextEdit()
        self.monitor_log_output.setReadOnly(True)
        self.monitor_log_output.setPlaceholderText("Monitoring logs...")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_monitor_button)
        button_layout.addStretch()

        controls_log_layout.addWidget(self.monitor_status_label)
        controls_log_layout.addLayout(button_layout)
        controls_log_layout.addWidget(QLabel("Log:"))
        controls_log_layout.addWidget(self.monitor_log_output)

        layout.addLayout(webcam_layout, 2) # Webcam takes more space
        layout.addLayout(controls_log_layout, 1)
        return page

    def create_blocking_page(self):
        """Creates the website blocking tab with parent password protection."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Website Blocking Controls")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # Status indicator
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        self.blocking_status = QLabel("Not Active")
        self.blocking_status.setStyleSheet("font-weight: bold; color: #dc3545;")
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.blocking_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Activate/Deactivate blocking
        action_group = QGroupBox("Blocking Controls")
        action_layout = QVBoxLayout(action_group)
        
        self.activate_blocking_btn = QPushButton("Activate Website Blocking")
        self.activate_blocking_btn.clicked.connect(self.activate_blocking)
        action_layout.addWidget(self.activate_blocking_btn)
        
        self.deactivate_blocking_btn = QPushButton("Deactivate Website Blocking")
        self.deactivate_blocking_btn.clicked.connect(self.deactivate_blocking)
        self.deactivate_blocking_btn.setStyleSheet("background-color: #dc3545;")
        action_layout.addWidget(self.deactivate_blocking_btn)
        
        layout.addWidget(action_group)
        
        # Browser extensions
        extensions_group = QGroupBox("Browser Extensions")
        extensions_layout = QVBoxLayout(extensions_group)
        
        self.setup_extensions_btn = QPushButton("Setup Browser Extensions")
        self.setup_extensions_btn.clicked.connect(self.setup_browser_extensions)
        extensions_layout.addWidget(self.setup_extensions_btn)
        
        layout.addWidget(extensions_group)
        
        # Persistent service 
        service_group = QGroupBox("Persistent Protection")
        service_layout = QVBoxLayout(service_group)
        
        service_info = QLabel("Install a background service to ensure website blocking remains active even after system restart.")
        service_info.setWordWrap(True)
        service_layout.addWidget(service_info)
        
        service_buttons = QHBoxLayout()
        
        self.install_service_btn = QPushButton("Install Service")
        self.install_service_btn.clicked.connect(self.install_blocking_service)
        service_buttons.addWidget(self.install_service_btn)
        
        self.remove_service_btn = QPushButton("Remove Service")
        self.remove_service_btn.clicked.connect(self.remove_blocking_service)
        self.remove_service_btn.setStyleSheet("background-color: #dc3545;")
        service_buttons.addWidget(self.remove_service_btn)
        
        service_layout.addLayout(service_buttons)
        layout.addWidget(service_group)
        
        # Blocked websites list
        sites_group = QGroupBox("Blocked Websites")
        sites_layout = QVBoxLayout(sites_group)
        
        self.sites_list = QListWidget()
        sites_layout.addWidget(self.sites_list)
        
        # Add some of the blocked sites to the list (just for display)
        for site in block_websites.blocked_sites[:20:2]:  # Get every other site from first 20
            self.sites_list.addItem(QListWidgetItem(site))
        
        # Add a "more sites are blocked" message
        more_item = QListWidgetItem("... and many more sites are blocked")
        more_item.setFlags(more_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        more_item.setForeground(QColor("#6c757d"))
        self.sites_list.addItem(more_item)
        
        # Test blocking
        test_button = QPushButton("Test Website Blocking")
        test_button.clicked.connect(self.test_website_blocking)
        sites_layout.addWidget(test_button)
        
        layout.addWidget(sites_group)
        
        # Status message at the bottom
        self.blocking_log = QTextEdit()
        self.blocking_log.setReadOnly(True)
        self.blocking_log.setMaximumHeight(100)
        self.blocking_log.setPlaceholderText("Activity log...")
        layout.addWidget(self.blocking_log)
        
        # Check and update blocking status
        self.update_blocking_status()
        
        return page

    def create_manage_page(self):
        """Creates the management tab for training faces and configuration."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Manage & Configure")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        # Training section
        train_group = QGroupBox("Face Recognition Training")
        train_layout = QVBoxLayout(train_group)

        # Create Dataset Button
        dataset_btn = QPushButton("Create Face Dataset")
        dataset_btn.clicked.connect(self.open_dataset_creator)
        train_layout.addWidget(dataset_btn)

        # Train Faces Button
        train_btn = QPushButton("Train Face Recognizer")
        train_btn.clicked.connect(self.run_training)
        train_layout.addWidget(train_btn)

        # Training log
        self.train_log = QTextEdit()
        self.train_log.setReadOnly(True)
        self.train_log.setMinimumHeight(100)
        train_layout.addWidget(self.train_log)

        layout.addWidget(train_group)

        # Add a stretch at the bottom
        layout.addStretch()

        # Status message at the bottom
        self.manage_status_label = QLabel("Ready")
        self.manage_status_label.setObjectName("statusLabel")
        layout.addWidget(self.manage_status_label)

        return page

    # --- Helper Methods --- 
    def set_status_color(self, label, status_type):
        palette = label.palette()
        if status_type == "running":
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#3498db"))
        elif status_type == "restricted":
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#e74c3c"))
        elif status_type == "safe":
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#2ecc71"))
        elif status_type == "error":
             palette.setColor(QPalette.ColorRole.WindowText, QColor("#f39c12"))
        else: # idle
            # Use the widget's default text color from its palette
            default_color = self.palette().color(QPalette.ColorRole.Text) 
            palette.setColor(QPalette.ColorRole.WindowText, default_color)
        label.setPalette(palette)

    def log_monitor(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.monitor_log_output.append(f"[{timestamp}] {message}")

    def log_training(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.train_log.append(f"[{timestamp}] {message}")

    def update_monitor_image(self, qt_image):
        try:
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.monitor_webcam_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.monitor_webcam_label.setPixmap(scaled_pixmap)
        except Exception as e:
             print(f"Error updating GUI image: {e}")

    def check_initial_files(self):
        # Check for models required for monitoring
        required_model_files = [
            os.path.join(MODELS_DIR, 'face_recognition_model.pkl'),
            os.path.join(MODELS_DIR, 'label_map.pkl'),
            os.path.join(MODELS_DIR, 'age_model.h5')
        ]
        missing_files = [f for f in required_model_files if not os.path.exists(f)]
        if missing_files:
            self.log_monitor("ERROR: Cannot start monitoring. Missing required model files:")
            relative_missing = [os.path.relpath(f, BASE_DIR) for f in missing_files]
            for f in relative_missing:
                self.log_monitor(f" - {f}")
            QMessageBox.critical(self, "Missing Files",
                                 "Monitoring cannot start due to missing model files:\n" +
                                 "\n".join([f" - {f}" for f in relative_missing]) +
                                 "\n\nPlease train the face recognizer or add the age model.")
            self.start_monitor_button.setEnabled(False)
            self.start_monitor_button.setToolTip("Missing model files required for monitoring.")
            return False
        self.start_monitor_button.setEnabled(True)
        self.start_monitor_button.setToolTip("")
        return True

    # --- Slots and Actions --- 
    def run_monitor_detection(self):
        if self.is_monitoring:
            self.log_monitor("Monitoring already in progress.")
            return
        if not self.check_initial_files(): # Re-check files before starting
             return

        self.is_monitoring = True
        self.start_monitor_button.setEnabled(False)
        self.start_monitor_button.setText("Monitoring...")
        self.monitor_status_label.setText("Status: Running Detection")
        self.set_status_color(self.monitor_status_label, "running")
        self.monitor_webcam_label.setText("Starting Webcam...")
        self.log_monitor("Starting monitoring thread...")

        self.monitor_thread = QThread()
        self.monitor_worker = Worker() # Use renamed worker
        self.monitor_worker.moveToThread(self.monitor_thread)

        self.monitor_worker.progress.connect(self.log_monitor)
        self.monitor_worker.result.connect(self.handle_monitor_result)
        self.monitor_worker.frame_update.connect(self.update_monitor_image)
        self.monitor_thread.started.connect(self.monitor_worker.run)
        self.monitor_worker.finished.connect(self.monitor_thread.quit)
        self.monitor_worker.finished.connect(self.monitor_worker.deleteLater)
        self.monitor_thread.finished.connect(self.monitor_thread.deleteLater)
        self.monitor_thread.finished.connect(self.on_monitor_finished)

        self.monitor_thread.start()

    def handle_monitor_result(self, is_restricted, detected_age, block_status, email_status):
        age_str = f"(Detected Age: {detected_age})" if detected_age != -1 else "(Age N/A)"
        if is_restricted:
            self.monitor_status_label.setText(f"Status: Child Detected {age_str}")
            self.set_status_color(self.monitor_status_label, "restricted")
            self.log_monitor(f"=> RESULT: Child Detected {age_str}.")
            self.log_monitor(f"   Block Result: {block_status}")
            self.log_monitor(f"   Email Result: {email_status}")
        else:
            if "error" in block_status.lower() or "error" in email_status.lower() or detected_age == -1:
                 self.monitor_status_label.setText(f"Status: Error/No Face {age_str}")
                 self.set_status_color(self.monitor_status_label, "error")
                 self.log_monitor(f"=> RESULT: Error occurred or age check failed {age_str}.")
                 self.log_monitor(f"   Block Result: {block_status}")
                 self.log_monitor(f"   Email Result: {email_status}")
            else:
                self.monitor_status_label.setText(f"Status: No Child Detected {age_str}")
                self.set_status_color(self.monitor_status_label, "safe")
                self.log_monitor(f"=> RESULT: No child detected {age_str}.")

    def on_monitor_finished(self):
        self.log_monitor("Monitoring thread finished.")
        self.is_monitoring = False
        if self.check_initial_files(): # Only re-enable if files are still valid
             self.start_monitor_button.setEnabled(True)
        self.start_monitor_button.setText("Start Monitoring")
        self.monitor_webcam_label.setText("Monitoring Stopped")
        self.monitor_webcam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def open_dataset_creator(self):
        self.log_training("Opening dataset creator...")
        # Create and execute the dialog
        dialog = DatasetCreatorDialog(self) # Pass parent

        # Check if the dialog initialized correctly (user entered # members)
        if not dialog.initialization_ok:
            self.log_training("Dataset creator initialization failed or was cancelled.")
            # Clean up the dialog object explicitly if exec() is not called
            dialog.deleteLater()
            return

        # Connect the signal before executing
        dialog.session_complete.connect(self.run_training)

        # Execute the dialog - this blocks until the dialog is closed
        # No need to check result code, signal handles success
        dialog.exec()
        self.log_training("Dataset creator dialog closed.")

    def run_training(self):
        if self.is_training:
            self.log_training("Training already in progress.")
            return
        # Potentially disable add face button during training
        self.start_monitor_button.setEnabled(False)
        self.is_training = True
        self.log_training("Starting training thread...")

        self.train_thread = QThread()
        self.train_worker = TrainWorker()
        self.train_worker.moveToThread(self.train_thread)

        self.train_worker.progress.connect(self.log_training)
        self.train_worker.finished.connect(self.handle_training_result)
        self.train_thread.started.connect(self.train_worker.run)
        self.train_worker.finished.connect(self.train_thread.quit)
        self.train_worker.finished.connect(self.train_worker.deleteLater)
        self.train_thread.finished.connect(self.train_thread.deleteLater)
        self.train_thread.finished.connect(self.on_training_finished)

        self.train_thread.start()

    def handle_training_result(self, success, message):
        self.log_training(f"=> RESULT: {message}")
        if success:
            QMessageBox.information(self, "Training Complete", message)
            self.check_initial_files() # Re-check files to potentially enable monitor button
        else:
            QMessageBox.warning(self, "Training Failed", message)

    def on_training_finished(self):
        self.log_training("Training thread finished.")
        self.is_training = False
        self.start_monitor_button.setEnabled(True)

    def open_blocking_tab(self):
        """Open the blocking tab with parent password authentication."""
        if PasswordDialog.get_password(self):
            self.stacked_widget.setCurrentIndex(1)
            self.blocking_button.setChecked(True)
            self.monitor_button.setChecked(False)
            self.manage_button.setChecked(False)
            
            # Log access
            self.log_blocking("Parent password verified - Access granted")
            
            # Update blocking status
            self.update_blocking_status()
        else:
            # If password verification failed or was cancelled, reset to previously selected tab
            current_index = self.stacked_widget.currentIndex()
            if current_index == 0:
                self.monitor_button.setChecked(True)
            elif current_index == 2:
                self.manage_button.setChecked(True)
            self.blocking_button.setChecked(False)

    def update_blocking_status(self):
        """Check if website blocking is active and update UI accordingly."""
        try:
            # Test a couple of sites to see if blocking is active
            test_results = []
            for site in ["pornhub.com", "xvideos.com"]:
                result = block_websites.test_site_blocking(site)
                test_results.append(result)
            
            if any("correctly redirected" in result for result in test_results):
                self.blocking_status.setText("Active")
                self.blocking_status.setStyleSheet("font-weight: bold; color: #198754;")
                self.log_blocking("Website blocking is currently active")
            else:
                self.blocking_status.setText("Not Active")
                self.blocking_status.setStyleSheet("font-weight: bold; color: #dc3545;")
                self.log_blocking("Website blocking is currently not active")
        except Exception as e:
            self.blocking_status.setText("Status Unknown")
            self.blocking_status.setStyleSheet("font-weight: bold; color: #fd7e14;")
            self.log_blocking(f"Error checking blocking status: {e}")

    def log_blocking(self, message):
        """Log a message to the blocking tab's log area."""
        timestamp = time.strftime("%H:%M:%S")
        self.blocking_log.append(f"[{timestamp}] {message}")

    def activate_blocking(self):
        """Activate website blocking."""
        try:
            self.log_blocking("Activating website blocking...")
            result = block_websites.block_sites()
            self.log_blocking(result)
            self.update_blocking_status()
            
            QMessageBox.information(
                self,
                "Blocking Activated",
                "Website blocking has been activated successfully."
            )
        except Exception as e:
            self.log_blocking(f"Error activating blocking: {e}")
            QMessageBox.warning(
                self,
                "Activation Error",
                f"Failed to activate website blocking: {e}"
            )

    def deactivate_blocking(self):
        """Deactivate website blocking."""
        # Require password confirmation for deactivation
        if PasswordDialog.get_password(self):
            try:
                self.log_blocking("Deactivating website blocking...")
                result = block_websites.unblock_sites()
                self.log_blocking(result)
                
                # Force additional DNS cache flush and browser cache notification
                try:
                    dns_result = block_websites.flush_dns_cache()
                    self.log_blocking(f"Additional DNS flush: {dns_result}")
                except Exception as e:
                    self.log_blocking(f"DNS flush error: {e}")
                
                # Update UI status
                self.update_blocking_status()
                
                # Create message with browser clearing instructions
                browser_msg = """
Websites have been unblocked at the system level, but you may need to:

1. Clear your browser's DNS cache:
   - Chrome/Edge: Go to chrome://net-internals/#dns and click "Clear host cache"
   - Firefox: Restart Firefox
   - Safari: Restart Safari

2. Clear your browser history/cache:
   - Most browsers: Press Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
   - Select "Cached images and files" and clear them

3. Restart your browser completely
"""
                
                QMessageBox.information(
                    self,
                    "Blocking Deactivated",
                    f"Website blocking has been deactivated successfully.\n\n{browser_msg}"
                )
            except Exception as e:
                self.log_blocking(f"Error deactivating blocking: {e}")
                QMessageBox.warning(
                    self,
                    "Deactivation Error",
                    f"Failed to deactivate website blocking: {e}"
                )
        else:
            self.log_blocking("Deactivation cancelled - Password verification failed")

    def setup_browser_extensions(self):
        """Set up browser extensions for additional blocking"""
        self.log_blocking("Setting up browser extensions...")
        result = browser_ext.setup_browser_extensions()
        
        if "status" in result:
            self.log_blocking(result["status"])
            
            if "instructions_file" in result:
                open_result = browser_ext.open_extension_instructions()
                self.log_blocking(open_result)
                
                QMessageBox.information(
                    self, 
                    "Browser Extensions Ready", 
                    "Browser extensions have been created. Follow the instructions in the opened file to install them."
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Browser Extensions Error", 
                    result["status"]
                )

    def install_blocking_service(self):
        """Install the persistent blocking service"""
        self.log_blocking("Installing blocking service...")
        result = block_service.create_service()
        self.log_blocking(result)
        
        if "✅" in result:
            QMessageBox.information(
                self, 
                "Service Installed", 
                "The blocking service has been installed successfully. Website blocking will persist across system reboots."
            )
        else:
            QMessageBox.warning(
                self, 
                "Service Installation Error", 
                f"Failed to install service: {result}"
            )

    def remove_blocking_service(self):
        """Remove the persistent blocking service"""
        # Require password confirmation for service removal
        if PasswordDialog.get_password(self):
            self.log_blocking("Removing blocking service...")
            result = block_service.remove_service()
            self.log_blocking(result)
            
            if "✅" in result:
                QMessageBox.information(
                    self, 
                    "Service Removed", 
                    "The blocking service has been removed successfully."
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Service Removal Error", 
                    f"Failed to remove service: {result}"
                )
        else:
            self.log_blocking("Service removal cancelled - Password verification failed")

    def test_website_blocking(self):
        """Test if website blocking is effective"""
        self.log_blocking("Testing website blocking...")
        test_sites = ["pornhub.com", "xvideos.com", "reddit.com", "facebook.com"]
        results = []
        
        for site in test_sites:
            result = block_websites.test_site_blocking(site)
            self.log_blocking(result)
            results.append(result)
        
        # Show the test results in a message box
        QMessageBox.information(
            self, 
            "Website Blocking Test Results", 
            "\n".join(results)
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Enable window decorations (minimize, maximize, close)
    app.setStyle("fusion")
    gui = MainAppGUI()
    gui.show()
    sys.exit(app.exec())
