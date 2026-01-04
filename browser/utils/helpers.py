"""
Helper functions for Modern Browser
"""

import os
import re
import hashlib
from datetime import datetime
from urllib.parse import urlparse, quote, unquote
from PyQt5.QtCore import QUrl


def is_valid_url(url_string):
    """Check if a string is a valid URL"""
    try:
        result = urlparse(url_string)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(url_string):
    """Normalize URL by adding scheme if missing"""
    url_string = url_string.strip()
    
    # Check if it's a search query
    if ' ' in url_string or not ('.' in url_string or url_string.startswith('localhost')):
        return None  # Return None to indicate it's a search query
    
    # Add scheme if missing
    if not url_string.startswith(('http://', 'https://', 'file://', 'about:')):
        url_string = 'https://' + url_string
    
    return url_string


def extract_domain(url_string):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url_string)
        domain = parsed.netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return url_string


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.2f} {size_names[i]}"


def format_timestamp(timestamp, format_str="%d.%m.%Y %H:%M"):
    """Format timestamp to human readable format"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except:
            return timestamp
    
    return timestamp.strftime(format_str)


def format_duration(seconds):
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def sanitize_filename(filename):
    """Sanitize filename by removing invalid characters"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Trim whitespace
    filename = filename.strip()
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    
    return filename or "download"


def generate_unique_filename(directory, filename):
    """Generate unique filename if file already exists"""
    if not os.path.exists(os.path.join(directory, filename)):
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while os.path.exists(os.path.join(directory, f"{name} ({counter}){ext}")):
        counter += 1
    
    return f"{name} ({counter}){ext}"


def hash_password(password, salt=None):
    """Hash password using PBKDF2 with SHA-256 for secure password storage"""
    if salt is None:
        salt = os.urandom(32)
    
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt + hashed


def verify_password(password, stored_hash):
    """Verify password against stored PBKDF2 hash"""
    salt = stored_hash[:32]
    stored_password = stored_hash[32:]
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return hashed == stored_password


def get_favicon_url(url_string):
    """Get favicon URL from a website URL"""
    try:
        parsed = urlparse(url_string)
        return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    except:
        return None


def is_internal_page(url):
    """Check if URL is an internal browser page"""
    if isinstance(url, QUrl):
        url = url.toString()
    
    return url.startswith(('about:', 'chrome:', 'browser:', 'data:'))


def truncate_text(text, max_length, suffix="..."):
    """Truncate text to max length with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_file_extension(url_or_path):
    """Get file extension from URL or path"""
    try:
        parsed = urlparse(url_or_path)
        path = parsed.path if parsed.path else url_or_path
        _, ext = os.path.splitext(path)
        return ext.lower()
    except:
        return ""


def mime_type_to_extension(mime_type):
    """Convert MIME type to file extension"""
    mime_map = {
        'text/html': '.html',
        'text/plain': '.txt',
        'text/css': '.css',
        'text/javascript': '.js',
        'application/javascript': '.js',
        'application/json': '.json',
        'application/pdf': '.pdf',
        'application/zip': '.zip',
        'application/x-rar-compressed': '.rar',
        'application/x-7z-compressed': '.7z',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        'image/svg+xml': '.svg',
        'video/mp4': '.mp4',
        'video/webm': '.webm',
        'audio/mpeg': '.mp3',
        'audio/wav': '.wav',
        'audio/ogg': '.ogg'
    }
    return mime_map.get(mime_type, '')


def escape_html(text):
    """Escape HTML special characters"""
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#39;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)


def get_color_for_security(is_secure):
    """Get color based on security status"""
    return "#34a853" if is_secure else "#ea4335"


def url_encode(text):
    """URL encode text"""
    return quote(text, safe='')


def url_decode(text):
    """URL decode text"""
    return unquote(text)
