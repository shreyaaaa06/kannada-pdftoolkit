import hashlib
import secrets
from datetime import datetime, timedelta
import json
import os

class AuthenticationManager:
    def __init__(self):
        self.users_file = 'users.json'
        self.sessions_file = 'sessions.json'
        self.init_default_users()
    
    def init_default_users(self):
        """Initialize with some default government employee accounts"""
        if not os.path.exists(self.users_file):
            default_users = {
                "admin": {
                    "password_hash": self.hash_password("admin123"),
                    "employee_id": "KGV001",
                    "name": "ನಿರ್ವಾಹಕ / Administrator",
                    "department": "ಮಾಹಿತಿ ತಂತ್ರಜ್ಞಾನ ವಿಭಾಗ",
                    "designation": "ಸಿಸ್ಟಮ್ ಅಡ್ಮಿನಿಸ್ಟ್ರೇಟರ್",
                    "role": "admin",
                    "created_at": datetime.now().isoformat()
                },
                "employee1": {
                    "password_hash": self.hash_password("emp123"),
                    "employee_id": "KGV002",
                    "name": "ರಾಜ್ ಕುಮಾರ್",
                    "department": "ರಾಜಸ್ವ ವಿಭಾಗ",
                    "designation": "ಸಹಾಯಕ ಕಮಿಷನರ್",
                    "role": "employee",
                    "created_at": datetime.now().isoformat()
                },
                "employee2": {
                    "password_hash": self.hash_password("emp123"),
                    "employee_id": "KGV003",
                    "name": "ಸುನೀತಾ ದೇವಿ",
                    "department": "ಶಿಕ್ಷಣ ವಿಭಾಗ",
                    "designation": "ಮುಖ್ಯ ಶಿಕ್ಷಣಾಧಿಕಾರಿ",
                    "role": "employee",
                    "created_at": datetime.now().isoformat()
                }
            }
            self.save_users(default_users)
    
    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return salt + password_hash.hex()
    
    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        salt = stored_hash[:32]
        stored_password_hash = stored_hash[32:]
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex() == stored_password_hash
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_users(self, users):
        """Save users to JSON file"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def load_sessions(self):
        """Load active sessions"""
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_sessions(self, sessions):
        """Save sessions to JSON file"""
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        users = self.load_users()
        
        if username not in users:
            return False, None
        
        user = users[username]
        if self.verify_password(password, user['password_hash']):
            return True, user
        
        return False, None
    
    def create_session(self, username):
        """Create a new session for authenticated user"""
        session_token = secrets.token_urlsafe(32)
        sessions = self.load_sessions()
        
        # Clean expired sessions
        self.clean_expired_sessions()
        
        # Create new session
        sessions[session_token] = {
            'username': username,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=8)).isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        self.save_sessions(sessions)
        return session_token
    
    def validate_session(self, session_token):
        """Validate session token and return user info"""
        if not session_token:
            return False, None
        
        sessions = self.load_sessions()
        
        if session_token not in sessions:
            return False, None
        
        session = sessions[session_token]
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.now() > expires_at:
            # Session expired
            del sessions[session_token]
            self.save_sessions(sessions)
            return False, None
        
        # Update last activity
        sessions[session_token]['last_activity'] = datetime.now().isoformat()
        self.save_sessions(sessions)
        
        # Get user info
        users = self.load_users()
        username = session['username']
        
        if username in users:
            return True, users[username]
        
        return False, None
    
    def logout_session(self, session_token):
        """Remove session (logout)"""
        sessions = self.load_sessions()
        
        if session_token in sessions:
            del sessions[session_token]
            self.save_sessions(sessions)
            return True
        
        return False
    
    def clean_expired_sessions(self):
        """Remove expired sessions"""
        sessions = self.load_sessions()
        current_time = datetime.now()
        
        expired_tokens = []
        for token, session in sessions.items():
            expires_at = datetime.fromisoformat(session['expires_at'])
            if current_time > expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del sessions[token]
        
        if expired_tokens:
            self.save_sessions(sessions)
    
    def get_user_info(self, username):
        """Get user information"""
        users = self.load_users()
        return users.get(username)
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        users = self.load_users()
        
        if username not in users:
            return False, "ಬಳಕೆದಾರ ಕಂಡುಬಂದಿಲ್ಲ"
        
        user = users[username]
        if not self.verify_password(old_password, user['password_hash']):
            return False, "ಪುರಾತನ ಪಾಸ್‌ವರ್ಡ್ ತಪ್ಪಾಗಿದೆ"
        
        # Update password
        users[username]['password_hash'] = self.hash_password(new_password)
        users[username]['password_changed_at'] = datetime.now().isoformat()
        
        self.save_users(users)
        return True, "ಪಾಸ್‌ವರ್ಡ್ ಯಶಸ್ವಿಯಾಗಿ ಬದಲಾಯಿಸಲಾಗಿದೆ"

    def register_user(self, email, password, name, employee_id=None, department=None, designation=None):
        """Register a new user"""
        import re
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "ಅಮಾನ್ಯ ಇಮೇಲ್ ವಿಳಾಸ"
        
        # Validate password strength
        if len(password) < 6:
            return False, "ಪಾಸ್‌ವರ್ಡ್ ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳಿರಬೇಕು"
        
        # Validate name
        if not name or len(name.strip()) < 2:
            return False, "ಮಾನ್ಯವಾದ ಹೆಸರು ನಮೂದಿಸಿ"
        
        users = self.load_users()
        
        # Check if email already exists
        for username, user_data in users.items():
            if user_data.get('email', '').lower() == email.lower():
                return False, "ಈ ಇಮೇಲ್ ವಿಳಾಸ ಈಗಾಗಲೇ ನೋಂದಾಯಿಸಲಾಗಿದೆ"
        
        # Generate username from email (part before @)
        base_username = email.split('@')[0].lower()
        username = base_username
        counter = 1
        
        # Ensure unique username
        while username in users:
            username = f"{base_username}{counter}"
            counter += 1
        
        # Create user data
        user_data = {
            "email": email.lower(),
            "password_hash": self.hash_password(password),
            "name": name.strip(),
            "employee_id": employee_id or f"USR{len(users) + 1:03d}",
            "department": department or "ಸಾಮಾನ್ಯ ಬಳಕೆದಾರ",
            "designation": designation or "ಬಳಕೆದಾರ",
            "role": "user",
            "created_at": datetime.now().isoformat(),
            "is_verified": False,
            "last_login": None
        }
        
        # Save user
        users[username] = user_data
        self.save_users(users)
        
        return True, f"ಖಾತೆ ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ! ನಿಮ್ಮ ಬಳಕೆದಾರ ಹೆಸರು: {username}"

    def email_exists(self, email):
        """Check if email already exists"""
        users = self.load_users()
        for user_data in users.values():
            if user_data.get('email', '').lower() == email.lower():
                return True
        return False

    def authenticate_user_by_email(self, email, password):
        """Authenticate user by email and password"""
        users = self.load_users()
        
        # Find user by email
        user_username = None
        for username, user_data in users.items():
            if user_data.get('email', '').lower() == email.lower():
                user_username = username
                break
        
        if not user_username:
            return False, None
        
        user = users[user_username]
        if self.verify_password(password, user['password_hash']):
            # Update last login
            users[user_username]['last_login'] = datetime.now().isoformat()
            self.save_users(users)
            return True, user
        
        return False, None
