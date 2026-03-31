import sqlite3
import os
from typing import Optional

class DatabaseConnection:
    """Database connection handler"""

    def __init__(self, db_path: str = "job_tracker.db"):
        self.db_path = db_path
        self._ensure_db_directory()

    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn

    def execute_script(self, script: str) -> bool:
        """Execute a SQL script"""
        try:
            with self.get_connection() as conn:
                conn.executescript(script)
                return True
        except Exception as e:
            print(f"Error executing script: {e}")
            return False

# Global connection instance
_db_connection = DatabaseConnection()

def get_connection():
    """Get database connection"""
    return _db_connection.get_connection()

def set_database_path(path: str):
    """Set the database path"""
    global _db_connection
    _db_connection = DatabaseConnection(path)
