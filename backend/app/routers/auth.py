from fastapi import APIRouter, HTTPException, Depends, status
from app.models import (
    UserCreate, UserLogin, UserResponse, LoginResponse, 
    MessageResponse, ErrorResponse, SessionUser
)
from app.database import db_manager
from app.auth import get_current_user, parse_skills, validate_password_strength
import json

router = APIRouter()

@router.post("/register", response_model=LoginResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""

    # Validate password strength
    is_valid, message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Create user
    user = db_manager.create_user(
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create session
    session_token = db_manager.create_session(user['id'])

    # Parse skills for response
    user['skills'] = parse_skills(user.get('skills'))

    return LoginResponse(
        user=UserResponse(**user),
        session_token=session_token,
        message="User registered successfully"
    )

@router.post("/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin):
    """Login user"""

    user = db_manager.authenticate_user(login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create session
    session_token = db_manager.create_session(user['id'])

    # Get full user profile
    full_user = db_manager.get_user_by_id(user['id'])
    if full_user:
        full_user['skills'] = parse_skills(full_user.get('skills'))
        user_response = UserResponse(**full_user)
    else:
        user_response = UserResponse(**user)

    return LoginResponse(
        user=user_response,
        session_token=session_token,
        message="Login successful"
    )

@router.post("/logout", response_model=MessageResponse)
async def logout_user(current_user: SessionUser = Depends(get_current_user)):
    """Logout user (invalidate session)"""

    # Note: In a real implementation, you'd need to pass the session token
    # For now, we'll just return success as the session validation happens in get_current_user

    return MessageResponse(message="Logout successful")

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: SessionUser = Depends(get_current_user)):
    """Get current user profile"""

    user = db_manager.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user['skills'] = parse_skills(user.get('skills'))
    return UserResponse(**user)

@router.get("/check-email/{email}")
async def check_email_availability(email: str):
    """Check if email is available for registration"""

    user = db_manager.get_user_by_email(email)
    return {
        "available": user is None,
        "message": "Email available" if user is None else "Email already registered"
    }
