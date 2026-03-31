"""
Pytest Configuration & Fixtures

This file provides common fixtures and configuration for all tests.
Fixtures help set up test data and environment for each test.
"""

import pytest
import sqlite3
import sys
import os
from pathlib import Path

# Add backend app to path so tests can import it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database.connection import DatabaseConnection, get_connection, set_database_path
from app.database.models import get_schema_script
from app.database.auth import AuthManager


@pytest.fixture(scope="session")
def test_db_path():
    """Provide path for test db"""
    return "/tmp/test_job_tracker.db"


@pytest.fixture(scope="session")
def setup_test_db(test_db_path):
    """
    Initialize test db with schema i.e: 
    create fresh test db, initializes all tables, & run once per test session
    """
    # Remove old test db if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Set db path for all tests
    set_database_path(test_db_path)
    
    # Create db connection
    conn = DatabaseConnection(test_db_path)
    
    # Execute schema script to create all tables
    schema = get_schema_script()
    conn.execute_script(schema)
    
    yield test_db_path
    
    # Cleanup after all tests (optional)
    # os.remove(test_db_path)


@pytest.fixture
def db_connection(setup_test_db):
    """
    Provide db connection for each test i.e:
    create a connection to test db, provide it to the test, & clean up after
    """
    conn = get_connection()
    yield conn
    conn.close()


@pytest.fixture
def clear_db_tables(db_connection):
    """
    Clear all tables before each test ensuring each test starts with clean state
    """
    cursor = db_connection.cursor()
    
    # Delete all data from tables (but keep table structure)
    tables = [
        'application_status_history',
        'job_applications',
        'user_sessions',
        'user_profiles',
        'users'
    ]
    
    for table in tables:
        cursor.execute(f'DELETE FROM {table}')
    
    db_connection.commit()
    yield


@pytest.fixture
def sample_user_data():
    """Provide sample user data for tests"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def sample_hashed_user(db_connection, sample_user_data):
    """
    Create a sample user in db
    
    Returns user data with hashed password already in db
    Also creates an empty profile for the user
    """
    cursor = db_connection.cursor()
    auth_manager = AuthManager()
    password_hash, salt = auth_manager.hash_password(sample_user_data["password"])
    
    cursor.execute('''
        INSERT INTO users (email, password_hash, salt, first_name, last_name, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        sample_user_data["email"],
        password_hash,
        salt,
        sample_user_data["first_name"],
        sample_user_data["last_name"],
        True
    ))
    
    db_connection.commit()
    user_id = cursor.lastrowid
    
    # Create empty profile for user
    cursor.execute('''
        INSERT INTO user_profiles (user_id) VALUES (?)
    ''', (user_id,))
    db_connection.commit()
    
    return {
        "id": user_id,
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
        "password_hash": password_hash,
        "first_name": sample_user_data["first_name"],
        "last_name": sample_user_data["last_name"]
    }


@pytest.fixture
def sample_job_application_data():
    """Provide sample job application data for tests"""
    return {
        "job_title": "Senior Python Developer",
        "company_name": "Tech Company Inc",
        "job_url": "https://example.com/job/123",
        "status": "applied",
        "notes": "Applied via online portal",
        "salary_range": "80k-120k",
        "location": "New York, NY",
        "employment_type": "full-time",
        "source": "api",
        "external_job_id": "external_123"
    }


@pytest.fixture
def sample_application_with_user(db_connection, sample_hashed_user, sample_job_application_data):
    """
    Create a complete application record for a user
    
    Returns dict. with application data and user ID
    """
    cursor = db_connection.cursor()
    
    cursor.execute('''
        INSERT INTO job_applications 
        (user_id, job_title, company_name, job_url, status, notes, salary_range, 
         location, employment_type, source, external_job_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        sample_hashed_user["id"],
        sample_job_application_data["job_title"],
        sample_job_application_data["company_name"],
        sample_job_application_data["job_url"],
        sample_job_application_data["status"],
        sample_job_application_data["notes"],
        sample_job_application_data["salary_range"],
        sample_job_application_data["location"],
        sample_job_application_data["employment_type"],
        sample_job_application_data["source"],
        sample_job_application_data["external_job_id"]
    ))
    
    db_connection.commit()
    application_id = cursor.lastrowid
    
    return {
        "id": application_id,
        "user_id": sample_hashed_user["id"],
        **sample_job_application_data
    }


@pytest.fixture
def mock_api_responses():
    """
    Provide mock responses for external API calls to mock external services
    """
    return {
        "himalayas_jobs": {
            "jobs": [
                {
                    "id": "1",
                    "title": "Python Developer",
                    "description": "Looking for Python, Django, and PostgreSQL skills",
                    "companyName": "Tech Corp",
                    "location": "Remote",
                    "salary": "100k-150k",
                    "url": "https://example.com/job/1"
                },
                {
                    "id": "2",
                    "title": "Python Backend Engineer",
                    "description": "Need Python, FastAPI, AWS expertise",
                    "companyName": "StartUp Inc",
                    "location": "San Francisco, CA",
                    "salary": "120k-180k",
                    "url": "https://example.com/job/2"
                }
            ]
        },
        "grammar_check": {
            "matches": [
                {
                    "message": "Spelling mistake",
                    "shortMessage": "Spelling",
                    "offset": 5,
                    "length": 5,
                    "replacements": [{"value": "correct"}]
                }
            ]
        },
        "resume_parser": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "skills": ["Python", "JavaScript", "SQL"],
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Senior Developer",
                    "duration": "2020-2024"
                }
            ]
        }
    }


@pytest.fixture
def api_client():
    """
    Provide FastAPI test client to allow endpoints testing minus actual HTTP calls
    """
    from fastapi.testclient import TestClient
    from app.main import app
    
    return TestClient(app)


# Custom Markers for organizing tests
def pytest_configure(config):
    """Register custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
