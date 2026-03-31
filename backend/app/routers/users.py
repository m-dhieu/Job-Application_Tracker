from fastapi import APIRouter, HTTPException, Depends, status
from app.models import (
    UserProfile, UserResponse, MessageResponse, SessionUser
)
from app.database import db_manager
from app.auth import get_current_user, parse_skills, serialize_skills

router = APIRouter()

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfile,
    current_user: SessionUser = Depends(get_current_user)
):
    """Update user profile"""

    # Prepare data for database
    update_data = {}

    if profile_data.phone is not None:
        update_data['phone'] = profile_data.phone
    if profile_data.location is not None:
        update_data['location'] = profile_data.location
    if profile_data.resume_path is not None:
        update_data['resume_path'] = profile_data.resume_path
    if profile_data.linkedin_url is not None:
        update_data['linkedin_url'] = profile_data.linkedin_url
    if profile_data.portfolio_url is not None:
        update_data['portfolio_url'] = profile_data.portfolio_url
    if profile_data.bio is not None:
        update_data['bio'] = profile_data.bio
    if profile_data.skills is not None:
        update_data['skills'] = serialize_skills(profile_data.skills)

    success = db_manager.update_user_profile(current_user.id, update_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )

    # Return updated user data
    user = db_manager.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user['skills'] = parse_skills(user.get('skills'))
    return UserResponse(**user)

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: SessionUser = Depends(get_current_user)):
    """Get user profile"""

    user = db_manager.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user['skills'] = parse_skills(user.get('skills'))
    return UserResponse(**user)
