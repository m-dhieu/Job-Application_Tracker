from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional, List
from app.models import (
    JobApplicationCreate, JobApplicationResponse, JobApplicationUpdate,
    ApplicationStatusUpdate, ApplicationStatusHistory, MessageResponse, SessionUser
)
from app.database import db_manager
from app.auth import get_current_user

router = APIRouter()

@router.post("/applications", response_model=JobApplicationResponse)
async def create_job_application(
    application_data: JobApplicationCreate,
    current_user: SessionUser = Depends(get_current_user)
):
    """Create a new job application"""

    app_data = {
        'job_title': application_data.job_title,
        'company_name': application_data.company_name,
        'job_url': application_data.job_url,
        'status': application_data.status.value,
        'notes': application_data.notes,
        'salary_range': application_data.salary_range,
        'location': application_data.location,
        'employment_type': application_data.employment_type.value if application_data.employment_type else None,
        'source': application_data.source,
        'external_job_id': application_data.external_job_id
    }

    application_id = db_manager.create_job_application(current_user.id, app_data)

    if not application_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create job application"
        )

    # Return the created application
    applications = db_manager.get_user_applications(current_user.id)
    application = next((app for app in applications if app['id'] == application_id), None)

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found after creation"
        )

    return JobApplicationResponse(**application)

@router.get("/applications", response_model=List[JobApplicationResponse])
async def get_user_applications(
    status: Optional[str] = Query(None, description="Filter by application status"),
    current_user: SessionUser = Depends(get_current_user)
):
    """Get all job applications for the current user"""

    applications = db_manager.get_user_applications(current_user.id, status)
    return [JobApplicationResponse(**app) for app in applications]

@router.get("/applications/{application_id}", response_model=JobApplicationResponse)
async def get_job_application(
    application_id: int,
    current_user: SessionUser = Depends(get_current_user)
):
    """Get a specific job application"""

    applications = db_manager.get_user_applications(current_user.id)
    application = next((app for app in applications if app['id'] == application_id), None)

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return JobApplicationResponse(**application)

@router.put("/applications/{application_id}/status", response_model=JobApplicationResponse)
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: SessionUser = Depends(get_current_user)
):
    """Update the status of a job application"""

    success = db_manager.update_application_status(
        application_id=application_id,
        user_id=current_user.id,
        new_status=status_update.status.value,
        notes=status_update.notes
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or update failed"
        )

    # Return updated application
    applications = db_manager.get_user_applications(current_user.id)
    application = next((app for app in applications if app['id'] == application_id), None)

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return JobApplicationResponse(**application)

@router.get("/applications/{application_id}/history", response_model=List[ApplicationStatusHistory])
async def get_application_history(
    application_id: int,
    current_user: SessionUser = Depends(get_current_user)
):
    """Get status history for a job application"""

    history = db_manager.get_application_history(application_id, current_user.id)
    return [ApplicationStatusHistory(**record) for record in history]

@router.delete("/applications/{application_id}", response_model=MessageResponse)
async def delete_job_application(
    application_id: int,
    current_user: SessionUser = Depends(get_current_user)
):
    """Delete a job application"""

    # First verify the application exists and belongs to the user
    applications = db_manager.get_user_applications(current_user.id)
    application = next((app for app in applications if app['id'] == application_id), None)

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Delete the application (this will cascade to delete related records)
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM job_applications WHERE id = ? AND user_id = ?', 
                          (application_id, current_user.id))

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found"
                )

            conn.commit()

        return MessageResponse(message="Application deleted successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application"
        )

@router.get("/applications/stats/summary")
async def get_application_stats(current_user: SessionUser = Depends(get_current_user)):
    """Get application statistics for the current user"""

    applications = db_manager.get_user_applications(current_user.id)

    # Calculate statistics
    total_applications = len(applications)
    status_counts = {}

    for app in applications:
        status = app['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    # Calculate this month's applications
    from datetime import datetime, timedelta
    current_month = datetime.now().replace(day=1)
    this_month_count = sum(
        1 for app in applications 
        if datetime.fromisoformat(app['application_date'].replace('Z', '+00:00')).replace(tzinfo=None) >= current_month
    )

    return {
        "total_applications": total_applications,
        "status_breakdown": status_counts,
        "this_month": this_month_count,
        "response_rate": round(
            (status_counts.get('interviewing', 0) + status_counts.get('accepted', 0)) / max(total_applications, 1) * 100, 1
        )
    }
