import os
import json
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')

class PasswordManager:
    def __init__(self):
        self.config = self._load_or_create_config()
        self.key = None
    
    def _load_or_create_config(self):
        """Load the configuration file or create a new one if it doesn't exist."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            
            config = {
                'password_hash': '',
                'salt': base64.b64encode(os.urandom(16)).decode('utf-8')
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            return config
    
    def _save_config(self):
        """Save the configuration to the file."""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)
    
    def _hash_password(self, password, salt=None):
        """Hash the password using SHA-256 with the given salt."""
        if salt is None:
            salt = base64.b64decode(self.config['salt'].encode('utf-8'))
        else:
            self.config['salt'] = base64.b64encode(salt).decode('utf-8')
        
        
        hash_obj = hashlib.sha256()
        hash_obj.update(password.encode('utf-8') + salt)
        return hash_obj.hexdigest()
    
    def _derive_key(self, password):
        """Derive an encryption key from the password using PBKDF2."""
        salt = base64.b64decode(self.config['salt'].encode('utf-8'))
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        return key
    
    def set_master_password(self, password):
        """Set the master password by hashing it and storing the hash."""
        salt = os.urandom(16)
        password_hash = self._hash_password(password, salt)
        self.config['password_hash'] = password_hash
        self._save_config()
        
        
        self.key = self._derive_key(password)
        return True
    
    def verify_password(self, password):
        """Verify if the given password matches the stored hash."""
        if not self.config['password_hash']:
            return False
        
        password_hash = self._hash_password(password)
        result = password_hash == self.config['password_hash']
        
        if result:
            
            self.key = self._derive_key(password)
        
        return result
    
    def has_master_password(self):
        """Check if a master password has been set."""
        return bool(self.config.get('password_hash', ''))
    
    def encrypt_data(self, data):
        """Encrypt the data using the derived key."""
        if not self.key:
            raise ValueError("Encryption key not set. Please verify the password first.")
        
        f = Fernet(self.key)
        return f.encrypt(data.encode('utf-8'))
    
    def decrypt_data(self, encrypted_data):
        """Decrypt the data using the derived key."""
        if not self.key:
            raise ValueError("Encryption key not set. Please verify the password first.")
        
        f = Fernet(self.key)
        return f.decrypt(encrypted_data).decode('utf-8')
    
    def generate_password(self, length=16):
        """Generate a secure random password."""
        return secrets.token_urlsafe(length)[:length] 