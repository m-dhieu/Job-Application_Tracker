from .manager import DatabaseManager
from .connection import get_connection
from .auth import AuthManager
from .users import UserManager
from .applications import ApplicationManager

# Global database instance
db_manager = DatabaseManager()

__all__ = [
    'DatabaseManager', 
    'db_manager', 
    'get_connection',
    'AuthManager',
    'UserManager', 
    'ApplicationManager'
]
