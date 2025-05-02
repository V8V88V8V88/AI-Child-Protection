import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from system_actions.password_manager import PasswordManager

class PasswordDialog(QDialog):
    def __init__(self, parent=None, setup_mode=False):
        super().__init__(parent)
        self.setup_mode = setup_mode
        self.password_manager = PasswordManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Parent Authentication" if not self.setup_mode else "Setup Parent Password")
        self.setFixedSize(400, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("Parent Authentication Required" if not self.setup_mode else "Setup Parent Password")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #0d6efd; padding-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Instruction label
        instruction_text = "Enter your parent password to access blocking controls:" if not self.setup_mode else "Create a parent password to secure blocking controls:"
        instruction_label = QLabel(instruction_text)
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Password field
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Enter password")
        layout.addWidget(self.password_field)
        
        # Confirm password field (only for setup mode)
        if self.setup_mode:
            self.confirm_password_field = QLineEdit()
            self.confirm_password_field.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_field.setPlaceholderText("Confirm password")
            layout.addWidget(self.confirm_password_field)
        
        # Show password checkbox
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.submit_button = QPushButton("Submit" if not self.setup_mode else "Create Password")
        self.submit_button.clicked.connect(self.process_password)
        self.submit_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def toggle_password_visibility(self, checked):
        if checked:
            self.password_field.setEchoMode(QLineEdit.EchoMode.Normal)
            if self.setup_mode:
                self.confirm_password_field.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
            if self.setup_mode:
                self.confirm_password_field.setEchoMode(QLineEdit.EchoMode.Password)
    
    def process_password(self):
        password = self.password_field.text()
        
        if not password:
            QMessageBox.warning(self, "Password Required", "Please enter a password.")
            return
        
        if self.setup_mode:
            confirm_password = self.confirm_password_field.text()
            
            if password != confirm_password:
                QMessageBox.warning(self, "Passwords Don't Match", "The passwords you entered do not match.")
                return
            
            if len(password) < 8:
                QMessageBox.warning(self, "Password Too Short", "Please use a password with at least 8 characters.")
                return
            
            # Set the master password
            self.password_manager.set_master_password(password)
            QMessageBox.information(self, "Password Created", "Parent password has been created successfully.")
            self.accept()
        else:
            # Verify the entered password
            if self.password_manager.verify_password(password):
                self.accept()
            else:
                QMessageBox.warning(self, "Incorrect Password", "The password you entered is incorrect.")
                self.password_field.clear()
                self.password_field.setFocus()
    
    @staticmethod
    def get_password(parent=None):
        """Show the password dialog and return True if the password is correct."""
        password_manager = PasswordManager()
        
        # Check if a password has been set
        if not password_manager.has_master_password():
            # First-time setup
            dialog = PasswordDialog(parent, setup_mode=True)
            result = dialog.exec()
            return result == QDialog.DialogCode.Accepted
        else:
            # Normal verification
            dialog = PasswordDialog(parent)
            result = dialog.exec()
            return result == QDialog.DialogCode.Accepted 