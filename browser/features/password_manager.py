"""
Password Manager for Modern Browser
"""

import json
import os
import base64
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from ..utils.constants import APP_NAME, APP_ORGANIZATION
from ..utils.helpers import extract_domain


class PasswordEntry:
    """Represents a saved password entry"""
    
    def __init__(self, domain, username, password, url=None):
        self.domain = domain
        self.username = username
        self.password = password
        self.url = url
        self.created_at = datetime.now().isoformat()
        self.last_used = None
        self.use_count = 0
    
    def to_dict(self):
        return {
            'domain': self.domain,
            'username': self.username,
            'password': self.password,  # This should be encrypted
            'url': self.url,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'use_count': self.use_count
        }
    
    @classmethod
    def from_dict(cls, data):
        entry = cls(
            domain=data.get('domain', ''),
            username=data.get('username', ''),
            password=data.get('password', ''),
            url=data.get('url')
        )
        entry.created_at = data.get('created_at', datetime.now().isoformat())
        entry.last_used = data.get('last_used')
        entry.use_count = data.get('use_count', 0)
        return entry


class PasswordManager(QObject):
    """Manages saved passwords with encryption"""
    
    # Signals
    password_saved = pyqtSignal(object)  # PasswordEntry
    password_removed = pyqtSignal(str, str)  # domain, username
    passwords_changed = pyqtSignal()
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        super().__init__()
        self._initialized = True
        self.settings = QSettings(APP_ORGANIZATION, APP_NAME)
        self.passwords = {}  # domain -> list of PasswordEntry
        self._fernet = None
        self._master_password_hash = None
        self._init_encryption()
        self._load()
    
    def _init_encryption(self):
        """Initialize encryption with stored or generated key"""
        # Get or generate salt
        stored_salt = self.settings.value("passwords/salt")
        if stored_salt:
            self._salt = base64.b64decode(stored_salt)
        else:
            self._salt = os.urandom(16)
            self.settings.setValue("passwords/salt", base64.b64encode(self._salt).decode())
        
        # Check for master password
        self._master_password_hash = self.settings.value("passwords/master_hash")
    
    def _derive_key(self, password):
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _hash_password(self, password):
        """Hash the master password for verification"""
        return hashlib.sha256((password + base64.b64encode(self._salt).decode()).encode()).hexdigest()
    
    def set_master_password(self, password):
        """Set the master password"""
        self._master_password_hash = self._hash_password(password)
        self.settings.setValue("passwords/master_hash", self._master_password_hash)
        
        key = self._derive_key(password)
        self._fernet = Fernet(key)
        
        # Re-encrypt all passwords
        self._save()
    
    def verify_master_password(self, password):
        """Verify the master password"""
        if not self._master_password_hash:
            return True  # No master password set
        
        return self._hash_password(password) == self._master_password_hash
    
    def unlock(self, password):
        """Unlock the password manager with master password"""
        if not self.verify_master_password(password):
            return False
        
        key = self._derive_key(password)
        self._fernet = Fernet(key)
        self._load()
        return True
    
    def is_locked(self):
        """Check if password manager is locked"""
        return self._master_password_hash is not None and self._fernet is None
    
    def has_master_password(self):
        """Check if master password is set"""
        return self._master_password_hash is not None
    
    def _encrypt(self, data):
        """Encrypt data"""
        if self._fernet:
            return self._fernet.encrypt(data.encode()).decode()
        return data  # No encryption if no master password
    
    def _decrypt(self, data):
        """Decrypt data"""
        if self._fernet:
            try:
                return self._fernet.decrypt(data.encode()).decode()
            except:
                return data
        return data
    
    def _load(self):
        """Load passwords from storage"""
        passwords_json = self.settings.value("passwords/entries", "{}")
        try:
            passwords_data = json.loads(passwords_json)
            self.passwords = {}
            for domain, entries in passwords_data.items():
                self.passwords[domain] = []
                for entry_data in entries:
                    entry = PasswordEntry.from_dict(entry_data)
                    # Decrypt password
                    entry.password = self._decrypt(entry.password)
                    self.passwords[domain].append(entry)
        except (json.JSONDecodeError, TypeError):
            self.passwords = {}
    
    def _save(self):
        """Save passwords to storage (encrypted)"""
        passwords_data = {}
        for domain, entries in self.passwords.items():
            passwords_data[domain] = []
            for entry in entries:
                entry_dict = entry.to_dict()
                # Encrypt password
                entry_dict['password'] = self._encrypt(entry.password)
                passwords_data[domain].append(entry_dict)
        
        self.settings.setValue("passwords/entries", json.dumps(passwords_data))
    
    def save_password(self, url, username, password):
        """Save a password for a URL"""
        domain = extract_domain(url)
        
        # Check if entry already exists
        if domain in self.passwords:
            for entry in self.passwords[domain]:
                if entry.username == username:
                    # Update existing
                    entry.password = password
                    entry.url = url
                    self._save()
                    self.password_saved.emit(entry)
                    self.passwords_changed.emit()
                    return entry
        else:
            self.passwords[domain] = []
        
        # Create new entry
        entry = PasswordEntry(domain, username, password, url)
        self.passwords[domain].append(entry)
        self._save()
        self.password_saved.emit(entry)
        self.passwords_changed.emit()
        return entry
    
    def get_password(self, url, username=None):
        """Get password for a URL and optional username"""
        domain = extract_domain(url)
        
        if domain not in self.passwords:
            return None
        
        entries = self.passwords[domain]
        
        if username:
            for entry in entries:
                if entry.username == username:
                    return entry
            return None
        
        # Return first entry if no username specified
        return entries[0] if entries else None
    
    def get_passwords_for_domain(self, domain):
        """Get all passwords for a domain"""
        return self.passwords.get(domain, [])
    
    def get_passwords_for_url(self, url):
        """Get all passwords for a URL"""
        domain = extract_domain(url)
        return self.get_passwords_for_domain(domain)
    
    def get_all_passwords(self):
        """Get all saved passwords"""
        all_entries = []
        for entries in self.passwords.values():
            all_entries.extend(entries)
        return all_entries
    
    def remove_password(self, domain, username):
        """Remove a password entry"""
        if domain in self.passwords:
            self.passwords[domain] = [
                e for e in self.passwords[domain] 
                if e.username != username
            ]
            if not self.passwords[domain]:
                del self.passwords[domain]
            self._save()
            self.password_removed.emit(domain, username)
            self.passwords_changed.emit()
            return True
        return False
    
    def update_password(self, domain, username, new_password):
        """Update a password"""
        if domain in self.passwords:
            for entry in self.passwords[domain]:
                if entry.username == username:
                    entry.password = new_password
                    self._save()
                    self.passwords_changed.emit()
                    return True
        return False
    
    def record_usage(self, domain, username):
        """Record password usage"""
        if domain in self.passwords:
            for entry in self.passwords[domain]:
                if entry.username == username:
                    entry.last_used = datetime.now().isoformat()
                    entry.use_count += 1
                    self._save()
                    return True
        return False
    
    def search(self, query):
        """Search passwords by domain or username"""
        query = query.lower()
        results = []
        for domain, entries in self.passwords.items():
            for entry in entries:
                if query in domain.lower() or query in entry.username.lower():
                    results.append(entry)
        return results
    
    def clear_all(self):
        """Clear all saved passwords"""
        self.passwords.clear()
        self._save()
        self.passwords_changed.emit()
    
    def export_passwords(self, filepath, master_password=None):
        """Export passwords to JSON file"""
        if master_password and not self.verify_master_password(master_password):
            return False
        
        data = {}
        for domain, entries in self.passwords.items():
            data[domain] = [entry.to_dict() for entry in entries]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    
    def import_passwords(self, filepath):
        """Import passwords from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for domain, entries in data.items():
            if domain not in self.passwords:
                self.passwords[domain] = []
            
            for entry_data in entries:
                entry = PasswordEntry.from_dict(entry_data)
                # Check for duplicates
                exists = any(
                    e.username == entry.username 
                    for e in self.passwords[domain]
                )
                if not exists:
                    self.passwords[domain].append(entry)
        
        self._save()
        self.passwords_changed.emit()
    
    def generate_password(self, length=16, include_special=True):
        """Generate a secure random password"""
        import secrets
        import string
        
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += string.punctuation
        
        password = ''.join(secrets.choice(chars) for _ in range(length))
        return password
    
    def get_count(self):
        """Get total number of saved passwords"""
        return sum(len(entries) for entries in self.passwords.values())
