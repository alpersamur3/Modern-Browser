import json
import os
import base64
import hashlib
import secrets
import logging
from datetime import datetime

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from ..utils.constants import APP_NAME, APP_ORGANIZATION
from ..utils.helpers import extract_domain

log = logging.getLogger(__name__)


class PasswordEntry:
    def __init__(self, domain, username, password, entry_id=None,
                 created_at=None, updated_at=None, notes=""):
        self.id = entry_id or secrets.token_hex(16)
        self.domain = domain
        self.username = username
        self.password = password
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.notes = notes

    def to_dict(self):
        return {
            'id': self.id, 'domain': self.domain, 'username': self.username,
            'password': self.password, 'created_at': self.created_at,
            'updated_at': self.updated_at, 'notes': self.notes,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            domain=data['domain'], username=data['username'],
            password=data['password'], entry_id=data.get('id'),
            created_at=data.get('created_at'), updated_at=data.get('updated_at'),
            notes=data.get('notes', ''),
        )


class PasswordManager(QObject):
    _instance = None

    password_saved = pyqtSignal(object)
    password_removed = pyqtSignal(str, str)
    passwords_changed = pyqtSignal()

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
        self._passwords = {}
        self._fernet = None
        self._master_set = False
        self._load()

    def _derive_key(self, master_password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32,
            salt=salt, iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key

    def _hash_master(self, master_password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32,
            salt=salt, iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode())).decode()

    def set_master_password(self, master_password):
        salt = os.urandom(16)
        key = self._derive_key(master_password, salt)
        self._fernet = Fernet(key)
        verify_hash = self._hash_master(master_password, salt)
        self.settings.setValue("passwords/salt", base64.b64encode(salt).decode())
        self.settings.setValue("passwords/verify", verify_hash)
        self._master_set = True
        self._re_encrypt_all()

    def verify_master_password(self, master_password):
        salt_b64 = self.settings.value("passwords/salt", "")
        stored_hash = self.settings.value("passwords/verify", "")
        if not salt_b64 or not stored_hash:
            return False
        salt = base64.b64decode(salt_b64)
        computed = self._hash_master(master_password, salt)
        if computed == stored_hash:
            key = self._derive_key(master_password, salt)
            self._fernet = Fernet(key)
            self._master_set = True
            self._decrypt_all()
            return True
        return False

    def has_master_password(self):
        return bool(self.settings.value("passwords/salt", ""))

    def is_unlocked(self):
        return self._master_set and self._fernet is not None

    def _encrypt(self, text):
        if self._fernet:
            return self._fernet.encrypt(text.encode()).decode()
        return text

    def _decrypt(self, text):
        if self._fernet:
            try:
                return self._fernet.decrypt(text.encode()).decode()
            except InvalidToken:
                log.warning("Şifre çözme başarısız")
                return None
        return text

    def _re_encrypt_all(self):
        for entry in self._passwords.values():
            entry.password = self._encrypt(entry.password)
        self._save()

    def _decrypt_all(self):
        for entry in self._passwords.values():
            decrypted = self._decrypt(entry.password)
            if decrypted is not None:
                entry.password = decrypted

    def _load(self):
        data = self.settings.value("passwords/data", "")
        if data:
            try:
                items = json.loads(data)
                for item in items:
                    entry = PasswordEntry.from_dict(item)
                    self._passwords[f"{entry.domain}:{entry.username}"] = entry
            except (json.JSONDecodeError, KeyError):
                log.warning("Parola verisi okunamadı")

    def _save(self):
        data = [e.to_dict() for e in self._passwords.values()]
        self.settings.setValue("passwords/data", json.dumps(data, ensure_ascii=False))

    def save_password(self, domain, username, password, notes=""):
        key = f"{domain}:{username}"
        stored_password = self._encrypt(password) if self._fernet else password
        entry = PasswordEntry(domain, username, stored_password, notes=notes)
        self._passwords[key] = entry
        self._save()
        self.password_saved.emit(entry)
        self.passwords_changed.emit()
        return entry

    def get_password(self, domain, username=None):
        if username:
            key = f"{domain}:{username}"
            entry = self._passwords.get(key)
            if entry:
                password = self._decrypt(entry.password) if self._fernet else entry.password
                return password
            return None
        results = []
        for entry in self._passwords.values():
            if entry.domain == domain:
                e_copy = PasswordEntry(
                    entry.domain, entry.username,
                    self._decrypt(entry.password) if self._fernet else entry.password,
                    entry_id=entry.id, created_at=entry.created_at,
                    updated_at=entry.updated_at, notes=entry.notes,
                )
                results.append(e_copy)
        return results

    def remove_password(self, domain, username):
        key = f"{domain}:{username}"
        if key in self._passwords:
            del self._passwords[key]
            self._save()
            self.password_removed.emit(domain, username)
            self.passwords_changed.emit()
            return True
        return False

    def update_password(self, domain, username, new_password, notes=None):
        key = f"{domain}:{username}"
        if key in self._passwords:
            entry = self._passwords[key]
            entry.password = self._encrypt(new_password) if self._fernet else new_password
            entry.updated_at = datetime.now().isoformat()
            if notes is not None:
                entry.notes = notes
            self._save()
            self.passwords_changed.emit()
            return True
        return False

    def get_all_domains(self):
        return list({e.domain for e in self._passwords.values()})

    def get_all_entries(self):
        return list(self._passwords.values())

    def search_passwords(self, query):
        q = query.lower()
        return [e for e in self._passwords.values() if q in e.domain.lower() or q in e.username.lower()]

    def generate_password(self, length=20):
        import string
        chars = string.ascii_letters + string.digits + string.punctuation
        while True:
            pwd = ''.join(secrets.choice(chars) for _ in range(length))
            if (any(c.isupper() for c in pwd) and any(c.islower() for c in pwd)
                    and any(c.isdigit() for c in pwd) and any(c in string.punctuation for c in pwd)):
                return pwd

    def get_password_count(self):
        return len(self._passwords)

    def clear_all(self):
        self._passwords.clear()
        self._save()
        self.passwords_changed.emit()

    def change_master_password(self, old_password, new_password):
        if not self.verify_master_password(old_password):
            return False
        decrypted = {}
        for key, entry in self._passwords.items():
            pwd = self._decrypt(entry.password)
            if pwd is None:
                return False
            decrypted[key] = pwd
        for key in decrypted:
            self._passwords[key].password = decrypted[key]
        self.set_master_password(new_password)
        return True
