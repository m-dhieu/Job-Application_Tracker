import sqlite3
from typing import Optional, Dict, Any
from .connection import get_connection
from .auth import AuthManager

class UserManager:
    """Handle user-related database operations"""

    def __init__(self):
        self.auth_manager = AuthManager()

    def create_user(self, email: str, password: str, first_name: str, last_name: str) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            password_hash, salt = self.auth_manager.hash_password(password)

            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (email, password_hash, salt, first_name, last_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (email, password_hash, salt, first_name, last_name))

                user_id = cursor.lastrowid

                # Create empty profile
                cursor.execute('''
                    INSERT INTO user_profiles (user_id) VALUES (?)
                ''', (user_id,))

                conn.commit()

                return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError:
            return None  # Email already exists

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.first_name, u.last_name, u.created_at, u.last_login,
                       p.phone, p.location, p.resume_path, p.linkedin_url, p.portfolio_url,
                       p.skills, p.bio
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
                WHERE u.id = ? AND u.is_active = TRUE
            ''', (user_id,))

            user = cursor.fetchone()
            return dict(user) if user else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.first_name, u.last_name, u.created_at, u.last_login,
                       p.phone, p.location, p.resume_path, p.linkedin_url, p.portfolio_url,
                       p.skills, p.bio
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
                WHERE u.email = ? AND u.is_active = TRUE
            ''', (email,))

            user = cursor.fetchone()
            return dict(user) if user else None

    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Build dynamic update query
                fields = []
                values = []
                for key, value in profile_data.items():
                    if key in ['phone', 'location', 'resume_path', 'linkedin_url', 'portfolio_url', 'skills', 'bio']:
                        fields.append(f"{key} = ?")
                        values.append(value)

                if fields:
                    fields.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(user_id)

                    query = f"UPDATE user_profiles SET {', '.join(fields)} WHERE user_id = ?"
                    cursor.execute(query, values)
                    conn.commit()

                return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET is_active = FALSE WHERE id = ?
                ''', (user_id,))

                # Invalidate all sessions for this user
                cursor.execute('''
                    UPDATE user_sessions SET is_active = FALSE WHERE user_id = ?
                ''', (user_id,))

                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deactivating user: {e}")
            return False
