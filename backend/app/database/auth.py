import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from .connection import get_connection

class AuthManager:
    """Handle authentication-related database operations"""

    @staticmethod
    def hash_password(password: str) -> Tuple[str, str]:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex(), salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == password_hash

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user login"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, email, password_hash, salt, first_name, last_name, is_active
                FROM users WHERE email = ?
            ''', (email,))

            user = cursor.fetchone()
            if user and user['is_active'] and self.verify_password(password, user['password_hash'], user['salt']):
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user['id'],))
                conn.commit()

                return dict(user)
            return None

    def create_session(self, user_id: int) -> str:
        """Create a new user session"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now().timestamp() + (24 * 60 * 60)  # 24 hours

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            conn.commit()

        return session_token

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user data"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.first_name, u.last_name
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = TRUE 
                AND s.expires_at > ? AND u.is_active = TRUE
            ''', (session_token, datetime.now().timestamp()))

            user = cursor.fetchone()
            return dict(user) if user else None

    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session (logout)"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_sessions SET is_active = FALSE WHERE session_token = ?
            ''', (session_token,))
            conn.commit()
            return cursor.rowcount > 0
