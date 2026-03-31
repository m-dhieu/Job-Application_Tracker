from fastapi import HTTPException, Header, status
from typing import Optional, Tuple
from app.database import db_manager
from app.models import SessionUser
import json

async def get_current_user(authorization: Optional[str] = Header(None)) -> SessionUser:
    """
    Get current user from session token
    Expected header format: "Bearer <session_token>"
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    user_data = db_manager.validate_session(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    return SessionUser(**user_data)

def parse_skills(skills_str: Optional[str]) -> Optional[list]:
    """Parse skills JSON string to list"""
    if not skills_str:
        return None
    try:
        return json.loads(skills_str)
    except (json.JSONDecodeError, TypeError):
        return None

def serialize_skills(skills: Optional[list]) -> Optional[str]:
    """Serialize skills list to JSON string"""
    if not skills:
        return None
    try:
        return json.dumps(skills)
    except (TypeError, ValueError):
        return None

def validate_email_format(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    # Check for at least one number or special character
    import re
    if not re.search(r'[0-9!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password should contain at least one number or special character"

    return True, "Password is valid"
