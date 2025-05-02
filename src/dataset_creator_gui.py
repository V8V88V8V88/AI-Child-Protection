import sys
import cv2
import os
# Comment out platform specific env var unless needed
# os.environ['QT_QPA_PLATFORM'] = 'xcb'
import time
from PyQt6.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, # Changed QWidget to QDialog
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QSizePolicy,
    QInputDialog
)
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal # Removed QCoreApplication, Added pyqtSignal

# Define base path relative to this script's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Inherit from QDialog instead of QWidget
class DatasetCreatorDialog(QDialog):
    # Signal emitted when all members specified in this session are done
    session_complete = pyqtSignal()

    # Accept parent argument for dialog behavior
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True) # Make it a modal dialog

        self.dataset_path = os.path.join(DATA_DIR, "family_dataset")
        self.member_name = ""
        self.member_folder = ""
        self.count = 0
        self.max_images = 10
        self.capture_active = False
        self.face_detected = False
        self.last_face_coords = None
        self.total_members_needed = 0
        self.members_completed = 0
        self.initialization_ok = True # Flag for successful init

        # Ask for number of members directly in constructor
        if not self.get_number_of_members():
            self.initialization_ok = False
            # Don't schedule exit, just return - dialog won't be shown
            return

        self.init_ui() # Now safe to init UI
        if not self.init_camera(): # Check if camera init failed
             self.initialization_ok = False
             return
        if not self.init_dataset_folder(): # Check if folder init failed
             self.initialization_ok = False
             return

    # get_number_of_members remains mostly the same
    def get_number_of_members(self):
        num, ok = QInputDialog.getInt(self, "Number of Members",
                                      "How many family members will you add in this session?",
                                      1, 1, 100, 1)
        if ok and num > 0:
            self.total_members_needed = num
            return True
        else:
            # Show warning but let the caller handle the failure
            QMessageBox.warning(self, "Input Required", "Number of members not specified. Aborting dataset creation.")
            return False

    # init_ui remains mostly the same
    def init_ui(self):
        self.setWindowTitle(f"Face Dataset Creator (0/{self.total_members_needed} Members Done)")
        self.setGeometry(100, 100, 800, 650)

        # --- Layouts ---
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        controls_layout = QVBoxLayout()
        status_layout = QHBoxLayout()

        # --- Widgets ---
        self.member_progress_label = QLabel(f"Adding Member {self.members_completed + 1} of {self.total_members_needed}")
        self.member_progress_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.name_label = QLabel("Enter Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(f"Name for member {self.members_completed + 1}")
        self.name_input.textChanged.connect(self.update_member_name)

        self.webcam_label = QLabel("Initializing Webcam...")
        self.webcam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.webcam_label.setMinimumSize(640, 480)
        self.webcam_label.setStyleSheet("border: 1px solid black; background-color: #333;")

        self.capture_button = QPushButton("Capture Image (0/10)")
        self.capture_button.setEnabled(False)
        self.capture_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.status_label = QLabel(f"Status: Enter name for member {self.members_completed + 1}.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_label = QLabel("Progress: 0/10")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # --- Assembling Layouts ---
        controls_layout.addWidget(self.member_progress_label)
        controls_layout.addWidget(self.name_label)
        controls_layout.addWidget(self.name_input)
        controls_layout.addWidget(self.capture_button)
        controls_layout.addStretch()

        top_layout.addWidget(self.webcam_label, 1)
        top_layout.addLayout(controls_layout)

        status_layout.addWidget(self.status_label, 1)
        status_layout.addWidget(self.progress_label)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(status_layout)

        self.setLayout(main_layout)

    # init_camera modified to return success/failure
    def init_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.show_error("Cannot open webcam.")
            self.capture_active = False
            self.webcam_label.setText("Error: Webcam not available.")
            return False # Indicate failure

        self.capture_active = True
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        return True # Indicate success

    # init_dataset_folder modified to return success/failure
    def init_dataset_folder(self):
        # Ensure the base DATA_DIR exists
        if not os.path.exists(DATA_DIR):
             try:
                 os.makedirs(DATA_DIR)
             except OSError as e:
                 self.show_error(f"Could not create data directory: {e}")
                 return False

        # Then ensure the specific dataset path within DATA_DIR exists
        if not os.path.exists(self.dataset_path):
            try:
                os.makedirs(self.dataset_path)
            except OSError as e:
                self.show_error(f"Could not create dataset directory: {e}")
                return False
        self.update_status(f"Using dataset directory: {self.dataset_path}")
        return True # Indicate success

    def update_member_name(self):
        # Only allow updates if session is not complete
        if self.members_completed >= self.total_members_needed:
            return

        current_name_input = self.name_input.text().strip()
        if current_name_input:
            # Check if this name is different from the last fully captured name (if any)
            # This logic assumes we reset self.member_name after successful capture
            if current_name_input != self.member_name:
                self.member_name = current_name_input
                self.member_folder = os.path.join(self.dataset_path, self.member_name)
                self.count = 0 # Reset image count for the new name
                self.update_status(f"Ready for {self.member_name} (Member {self.members_completed + 1}).") # Simplified status

                self.update_capture_button_state()
            # If name hasn't changed, do nothing here, allow capture button state update

        else: # Name input is empty
            self.member_name = ""
            self.member_folder = ""
            self.update_status(f"Status: Enter name for member {self.members_completed + 1}.")
            self.capture_button.setEnabled(False)

        # Update progress label regardless of name change, it depends on self.count
        self.update_progress_label()

    def update_frame(self):
        if not self.capture_active or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.update_status("Error: Cannot read frame from webcam.")
            time.sleep(0.1)
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))

        self.face_detected = len(faces) > 0
        status_prefix = f"Member {self.members_completed + 1}/{self.total_members_needed}: "
        if self.members_completed >= self.total_members_needed:
             status_prefix = "Session Complete: "

        current_status = ""

        if self.face_detected:
            (x, y, w, h) = max(faces, key=lambda item: item[2] * item[3])
            self.last_face_coords = (x, y, w, h)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            if self.member_name and self.count < self.max_images:
                 current_status = f"{status_prefix}Ready for {self.member_name}."
            elif not self.member_name:
                 current_status = f"{status_prefix}Enter name."
            else: # Max images reached for this member
                current_status = f"{status_prefix}{self.member_name} done. Waiting for next step."
        else:
            self.last_face_coords = None
            if self.member_name:
                 current_status = f"{status_prefix}Point camera at face for {self.member_name}."
            else:
                 current_status = f"{status_prefix}Enter name for member {self.members_completed + 1}."

        if self.members_completed >= self.total_members_needed:
             current_status = "Session Complete. You can close the window."

        self.update_status(current_status)
        self.update_capture_button_state()

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.webcam_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.webcam_label.setPixmap(scaled_pixmap)

    def update_capture_button_state(self):
        # Enable capture only if name is entered, face is detected, not max images, and session not complete
        can_capture = (bool(self.member_name) and
                       self.face_detected and
                       self.count < self.max_images and
                       self.members_completed < self.total_members_needed)
        self.capture_button.setEnabled(can_capture)

    def update_progress_label(self):
        self.progress_label.setText(f"Progress: {self.count}/{self.max_images}")

    # capture_image modified to emit signal and accept dialog on completion
    def capture_image(self):
        if not self.member_folder or not self.face_detected or self.last_face_coords is None:
            self.update_status("Cannot capture: Ensure name is entered and face is detected.")
            return

        # --- Start Addition ---
        # Create the member folder right before saving the first image
        if not os.path.exists(self.member_folder):
            try:
                os.makedirs(self.member_folder)
                self.update_status(f"Created folder for {self.member_name}. Capturing image 1...")
            except OSError as e:
                self.show_error(f"Could not create folder {self.member_folder}: {e}")
                return # Don't proceed if folder creation fails
        # --- End Addition ---

        if self.count >= self.max_images:
             self.update_status(f"Already captured {self.max_images} images for {self.member_name}.")
             return
        if self.members_completed >= self.total_members_needed:
             self.update_status("Session already complete.")
             return

        ret, frame = self.cap.read()
        if not ret:
            self.show_error("Failed to grab frame for capture.")
            return

        (x, y, w, h) = self.last_face_coords
        face_image = frame[y:y + h, x:x + w]

        image_name = f"{self.member_name}_{int(time.time())}_{self.count}.jpg"
        img_save_path = os.path.join(self.member_folder, image_name)
        try:
            cv2.imwrite(img_save_path, face_image)
            self.count += 1
            self.update_status(f"Saved image {self.count}/{self.max_images} for {self.member_name}")
            self.update_progress_label()
        except Exception as e:
            self.show_error(f"Error saving image {img_save_path}: {e}")
            # Don't proceed if save failed
            return

        # --- Check for Member/Session Completion ---
        if self.count >= self.max_images:
            self.members_completed += 1
            last_member_name = self.member_name
            self.member_name = "" # Reset current member name
            self.name_input.clear() # Clear input field
            self.capture_button.setEnabled(False) # Disable until new name/face
            self.setWindowTitle(f"Face Dataset Creator ({self.members_completed}/{self.total_members_needed} Members Done)")

            if self.members_completed >= self.total_members_needed:
                # Session Complete
                self.update_status("Session Complete! All members added.")
                self.name_input.setPlaceholderText("Session Complete")
                self.name_input.setEnabled(False)
                self.capture_button.setEnabled(False)
                self.member_progress_label.setText(f"Finished: {self.members_completed}/{self.total_members_needed} Members Added")
                QMessageBox.information(self, "Session Complete",
                                        f"Successfully captured images for all {self.total_members_needed} members.")
                # Emit signal and close dialog with Accepted status
                self.session_complete.emit()
                self.accept() # Close dialog with Accepted status
            else:
                # Member Complete, prompt for next
                next_member_num = self.members_completed + 1
                self.update_status(f"Member '{last_member_name}' complete. Enter name for member {next_member_num}.")
                self.name_input.setPlaceholderText(f"Name for member {next_member_num}")
                self.member_progress_label.setText(f"Adding Member {next_member_num} of {self.total_members_needed}")
                QMessageBox.information(self, f"Member {self.members_completed} Complete",
                                        f"Successfully captured {self.max_images} images for {last_member_name}.\nPlease enter the name for the next member ({next_member_num}/{self.total_members_needed}).")

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")

    def show_error(self, message):
        self.update_status(f"Error: {message}")
        QMessageBox.critical(self, "Error", message)

    # Override closeEvent to stop timer and release camera
    def closeEvent(self, event):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        if self.capture_active and hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            print("Dataset creator webcam released.")
        super().closeEvent(event)

    # Override reject to ensure resources are released if user cancels
    def reject(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        if self.capture_active and hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            print("Dataset creator webcam released on cancel.")
        super().reject()

# Remove the __main__ block as this is no longer a standalone app
# if __name__ == '__main__':
#     ...

# if __name__ == '__main__':
#     if not os.path.exists(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'):
#          print("ERROR: Haar cascade file not found. Please ensure OpenCV is installed correctly.")
#          sys.exit(1)

#     app = QApplication(sys.argv)

#     # Create the GUI instance. The __init__ method will handle asking for the number of members.
#     gui = DatasetCreatorGUI()

#     # If the user cancelled the initial dialog, gui.__init__ might have requested an exit.
#     # We check if the GUI object was fully initialized (e.g., check if total_members_needed is set)
#     # or rely on the QTimer exit scheduled in __init__ if get_number_of_members failed.
#     if hasattr(gui, 'total_members_needed') and gui.total_members_needed > 0: # Only show if setup was successful
#         gui.show()
#         sys.exit(app.exec())
#     else:
#         # Allow the QTimer scheduled in __init__ to quit the application gracefully
#         # This case happens if get_number_of_members returned False
#         # We might not need an explicit exit here if the timer handles it.
#         # sys.exit(0) # Or just let the timer handle the exit
#         pass # Let the scheduled exit run 