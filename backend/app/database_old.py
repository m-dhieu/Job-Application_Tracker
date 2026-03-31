import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import hashlib
import secrets

class DatabaseManager:
    def __init__(self, db_path: str = "job_tracker.db"):
        """Initialize database manager with SQLite database"""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn

    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            # User profiles table for additional info
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    phone TEXT,
                    location TEXT,
                    resume_path TEXT,
                    linkedin_url TEXT,
                    portfolio_url TEXT,
                    skills TEXT,  -- JSON string of skills array
                    bio TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Job applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_title TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    job_url TEXT,
                    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'applied',  -- applied, interviewing, rejected, accepted
                    notes TEXT,
                    salary_range TEXT,
                    location TEXT,
                    employment_type TEXT,
                    source TEXT DEFAULT 'manual',  -- manual, api, scraper
                    external_job_id TEXT,  -- For tracking external API job IDs
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Application status history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS application_status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (application_id) REFERENCES job_applications (id) ON DELETE CASCADE
                )
            ''')

            # User sessions for authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            conn.commit()

    def hash_password(self, password: str) -> tuple[str, str]:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex(), salt

    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == password_hash

    def create_user(self, email: str, password: str, first_name: str, last_name: str) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            password_hash, salt = self.hash_password(password)

            with self.get_connection() as conn:
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

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user login"""
        with self.get_connection() as conn:
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

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
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
        with self.get_connection() as conn:
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
            with self.get_connection() as conn:
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

    def create_job_application(self, user_id: int, application_data: Dict[str, Any]) -> Optional[int]:
        """Create a new job application"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO job_applications 
                    (user_id, job_title, company_name, job_url, status, notes, salary_range, 
                     location, employment_type, source, external_job_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    application_data.get('job_title'),
                    application_data.get('company_name'),
                    application_data.get('job_url'),
                    application_data.get('status', 'applied'),
                    application_data.get('notes'),
                    application_data.get('salary_range'),
                    application_data.get('location'),
                    application_data.get('employment_type'),
                    application_data.get('source', 'manual'),
                    application_data.get('external_job_id')
                ))

                application_id = cursor.lastrowid

                # Add initial status history
                cursor.execute('''
                    INSERT INTO application_status_history (application_id, status, notes)
                    VALUES (?, ?, ?)
                ''', (application_id, application_data.get('status', 'applied'), 'Application created'))

                conn.commit()
                return application_id
        except Exception as e:
            print(f"Error creating application: {e}")
            return None

    def get_user_applications(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all applications for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT * FROM job_applications 
                WHERE user_id = ?
            '''
            params = [user_id]

            if status:
                query += ' AND status = ?'
                params.append(status)

            query += ' ORDER BY application_date DESC'

            cursor.execute(query, params)
            applications = cursor.fetchall()

            return [dict(app) for app in applications]

    def update_application_status(self, application_id: int, user_id: int, new_status: str, notes: str = None) -> bool:
        """Update application status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Verify application belongs to user
                cursor.execute('''
                    SELECT id FROM job_applications WHERE id = ? AND user_id = ?
                ''', (application_id, user_id))

                if not cursor.fetchone():
                    return False

                # Update application status
                cursor.execute('''
                    UPDATE job_applications SET status = ? WHERE id = ?
                ''', (new_status, application_id))

                # Add status history
                cursor.execute('''
                    INSERT INTO application_status_history (application_id, status, notes)
                    VALUES (?, ?, ?)
                ''', (application_id, new_status, notes))

                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating application status: {e}")
            return False

    def get_application_history(self, application_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get status history for an application"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ash.* FROM application_status_history ash
                JOIN job_applications ja ON ash.application_id = ja.id
                WHERE ash.application_id = ? AND ja.user_id = ?
                ORDER BY ash.changed_at DESC
            ''', (application_id, user_id))

            history = cursor.fetchall()
            return [dict(record) for record in history]

    def create_session(self, user_id: int) -> str:
        """Create a new user session"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now().timestamp() + (24 * 60 * 60)  # 24 hours

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            conn.commit()

        return session_token

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user data"""
        with self.get_connection() as conn:
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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_sessions SET is_active = FALSE WHERE session_token = ?
            ''', (session_token,))
            conn.commit()
            return cursor.rowcount > 0

# Global database instance
db_manager = DatabaseManager()
