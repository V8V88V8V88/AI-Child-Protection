import sys
import os
import time
import cv2
import numpy as np
from face_operations import detector as face_detector
from face_operations import training as face_trainer
from system_actions import host_blocker as block_websites
from system_actions import email_notifier as emailalert
from dataset_creator_gui import DatasetCreatorDialog
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QDialog,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox, QSizePolicy, QStackedWidget,
    QFrame
)
from PyQt6.QtGui import QFont, QColor, QPalette, QImage, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QSize

# Define base path relative to this script's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- Modern Stylesheet (Example - Refine as needed) ---
MODERN_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f8f9fa; /* Light background */
    color: #212529; /* Dark text */
    font-family: "Segoe UI", Arial, sans-serif; /* Modern font */
}
QWidget#sidebar {
    background-color: #e9ecef; /* Slightly darker sidebar */
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
    background-color: #0d6efd; /* Bootstrap primary blue */
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
    background-color: #6c757d; /* Bootstrap secondary grey */
    color: #e9ecef;
}
QTextEdit {
    background-color: #ffffff; /* White background for text edit */
    border: 1px solid #ced4da; /* Subtle border */
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

# Main Application Window (QMainWindow for more flexibility if needed)
class MainAppGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.is_training = False
        self.monitor_thread = None
        self.monitor_worker = None
        self.train_thread = None
        self.train_worker = None
        self.init_ui()
        self.check_initial_files() # Check files on startup

    def init_ui(self):
        self.setWindowTitle("AI Child Protection")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(MODERN_STYLESHEET)

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

        self.manage_button = QPushButton("👤 Manage Faces")
        self.manage_button.setObjectName("navButton")
        self.manage_button.setCheckable(True)
        self.manage_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        sidebar_layout.addWidget(QLabel("Navigation")) # Simple title for sidebar
        sidebar_layout.addWidget(self.monitor_button)
        sidebar_layout.addWidget(self.manage_button)
        sidebar_layout.addStretch()

        # --- Create Pages --- 
        self.monitor_page = self.create_monitor_page()
        self.manage_page = self.create_manage_page()

        self.stacked_widget.addWidget(self.monitor_page)
        self.stacked_widget.addWidget(self.manage_page)

        # --- Assemble Main Layout --- 
        main_hbox.addWidget(sidebar)
        main_hbox.addWidget(self.stacked_widget)

        # Set initial state
        self.monitor_button.setChecked(True)
        self.stacked_widget.setCurrentIndex(0)

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

    def create_manage_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Manage Face Data")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Add button
        self.add_face_button = QPushButton("➕ Add New Person")
        self.add_face_button.setIconSize(QSize(16,16)) # Optional icon size
        self.add_face_button.clicked.connect(self.open_dataset_creator)
        self.add_face_button.setFixedWidth(200) # Fixed width for button
        layout.addWidget(self.add_face_button)

        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Training Status/Log
        layout.addWidget(QLabel("Training Status:"))
        self.training_log_output = QTextEdit()
        self.training_log_output.setReadOnly(True)
        self.training_log_output.setFixedHeight(200) # Limit height
        self.training_log_output.setPlaceholderText("Training logs will appear here after adding a person...")
        layout.addWidget(self.training_log_output)

        layout.addStretch()
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
        self.training_log_output.append(f"[{timestamp}] {message}")

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
        self.add_face_button.setEnabled(False)
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
        self.add_face_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainAppGUI()
    gui.show()
    sys.exit(app.exec())
