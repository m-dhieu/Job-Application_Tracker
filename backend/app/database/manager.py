from typing import Optional, List, Dict, Any, Tuple
from .connection import get_connection, set_database_path
from .models import ALL_TABLES
from .auth import AuthManager
from .users import UserManager
from .applications import ApplicationManager

class DatabaseManager:
    """Main database manager that combines all database operations"""

    def __init__(self, db_path: str = "job_tracker.db"):
        """Initialize database manager with SQLite database"""
        self.db_path = db_path
        if db_path != "job_tracker.db":
            set_database_path(db_path)

        # Initialize managers
        self.auth_manager = AuthManager()
        self.user_manager = UserManager()
        self.application_manager = ApplicationManager()

        # Initialize database
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        with get_connection() as conn:
            cursor = conn.cursor()
            for table_sql in ALL_TABLES:
                cursor.execute(table_sql)
            conn.commit()

    # Authentication methods
    def hash_password(self, password: str) -> Tuple[str, str]:
        """Hash password with salt"""
        return self.auth_manager.hash_password(password)

    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        return self.auth_manager.verify_password(password, password_hash, salt)

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user login"""
        return self.auth_manager.authenticate_user(email, password)

    def create_session(self, user_id: int) -> str:
        """Create a new user session"""
        return self.auth_manager.create_session(user_id)

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user data"""
        return self.auth_manager.validate_session(session_token)

    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session (logout)"""
        return self.auth_manager.invalidate_session(session_token)

    # User management methods
    def create_user(self, email: str, password: str, first_name: str, last_name: str) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        return self.user_manager.create_user(email, password, first_name, last_name)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.user_manager.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.user_manager.get_user_by_email(email)

    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        return self.user_manager.update_user_profile(user_id, profile_data)

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account"""
        return self.user_manager.deactivate_user(user_id)

    # Application management methods
    def create_job_application(self, user_id: int, application_data: Dict[str, Any]) -> Optional[int]:
        """Create a new job application"""
        return self.application_manager.create_job_application(user_id, application_data)

    def get_user_applications(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all applications for a user"""
        return self.application_manager.get_user_applications(user_id, status)

    def get_application_by_id(self, application_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific application by ID"""
        return self.application_manager.get_application_by_id(application_id, user_id)

    def update_application_status(self, application_id: int, user_id: int, new_status: str, notes: str = None) -> bool:
        """Update application status"""
        return self.application_manager.update_application_status(application_id, user_id, new_status, notes)

    def update_application(self, application_id: int, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update application details"""
        return self.application_manager.update_application(application_id, user_id, update_data)

    def delete_application(self, application_id: int, user_id: int) -> bool:
        """Delete a job application"""
        return self.application_manager.delete_application(application_id, user_id)

    def get_application_history(self, application_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get status history for an application"""
        return self.application_manager.get_application_history(application_id, user_id)

    def get_application_stats(self, user_id: int) -> Dict[str, Any]:
        """Get application statistics for a user"""
        return self.application_manager.get_application_stats(user_id)

    # Utility methods
    def get_connection(self):
        """Get database connection (for backward compatibility)"""
        return get_connection()
