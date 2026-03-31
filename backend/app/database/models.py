"""Database schema definitions and table creation SQL"""

# Users table
CREATE_USERS_TABLE = '''
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
'''

# User profiles table
CREATE_USER_PROFILES_TABLE = '''
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
'''

# Job applications table
CREATE_JOB_APPLICATIONS_TABLE = '''
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
'''

# Application status history table
CREATE_APPLICATION_STATUS_HISTORY_TABLE = '''
CREATE TABLE IF NOT EXISTS application_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (application_id) REFERENCES job_applications (id) ON DELETE CASCADE
)
'''

# User sessions table
CREATE_USER_SESSIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
'''

# All table creation statements
ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_USER_PROFILES_TABLE,
    CREATE_JOB_APPLICATIONS_TABLE,
    CREATE_APPLICATION_STATUS_HISTORY_TABLE,
    CREATE_USER_SESSIONS_TABLE
]

def get_schema_script() -> str:
    """Get the complete database schema as a single script"""
    return ';\n'.join(ALL_TABLES) + ';'
