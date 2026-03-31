import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from app.services.job_service import fetch_jobs
from app.services.skill_service import extract_skills_from_job, analyze_skills_demand, get_skill_recommendations
from app.services.resource_service import fetch_resources

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def get_jobs(limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    """
    Fetch jobs from external API with pagination.
    """
    try:
        # Return just job list (use .get if API returns a dict)
        jobs = fetch_jobs(limit, offset)
        return {"jobs": jobs}
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch jobs from external API: {e}")

@router.get("/search")
def search_jobs_with_skills(
    query: str = Query(..., min_length=2, description="Search query for jobs"),
    limit: int = Query(10, ge=1, le=20, description="Number of jobs to return"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Search for jobs and return results with extracted skills and learning resources.
    """
    try:
        # Fetch jobs from external API
        jobs = fetch_jobs(limit, offset)

        # Filter jobs based on search query
        filtered_jobs = []
        for job in jobs:
            job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('companyName', '')}".lower()
            if query.lower() in job_text:
                filtered_jobs.append(job)

        # Extract skills from each job
        jobs_with_skills = []
        all_skills = []

        for job in filtered_jobs:
            job_skills = extract_skills_from_job(job)
            job_with_skills = {
                **job,
                "required_skills": job_skills
            }
            jobs_with_skills.append(job_with_skills)
            all_skills.extend(job_skills)

        # Analyze skill demand across all jobs
        skill_demand = analyze_skills_demand(filtered_jobs)

        # Get top skills from search results
        top_skills = list(skill_demand.keys())[:10]

        # Fetch learning resources for top skills
        resources_by_skill = {}
        for skill in top_skills[:5]:  # Limit to top 5 skills to avoid too many API calls
            try:
                resources = fetch_resources(skill)
                if resources:
                    resources_by_skill[skill] = resources[:3]  # Limit to 3 resources per skill
            except Exception as e:
                logger.warning(f"Failed to fetch resources for skill {skill}: {e}")
                resources_by_skill[skill] = []

        # Get skill recommendations
        unique_skills = list(set(all_skills))
        recommendations = get_skill_recommendations(unique_skills, skill_demand)

        return {
            "query": query,
            "total_jobs": len(jobs_with_skills),
            "jobs": jobs_with_skills,
            "skills_analysis": {
                "top_skills": [{"skill": skill, "demand": count} for skill, count in list(skill_demand.items())[:10]],
                "total_unique_skills": len(skill_demand),
                "skill_recommendations": recommendations
            },
            "learning_resources": resources_by_skill,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(filtered_jobs) == limit
            }
        }

    except Exception as e:
        logger.error(f"Error in job search with skills: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to search jobs: {e}")

@router.get("/{job_id}/skills")
def get_job_skills(job_id: str):
    """
    Get skills for a specific job by fetching job details and extracting skills.
    """
    try:
        # For this example, we'll fetch recent jobs and find the matching one
        # In a real implementation, you'd have a proper job details endpoint
        jobs = fetch_jobs(50, 0)  # Fetch more jobs to find the specific one

        target_job = None
        for job in jobs:
            # Match by title or company name (since we don't have actual job IDs from the API)
            if (job_id.lower() in job.get('title', '').lower() or
                job_id.lower() in job.get('companyName', '').lower()):
                target_job = job
                break

        if not target_job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Extract skills from the job
        job_skills = extract_skills_from_job(target_job)

        # Fetch learning resources for each skill
        resources_by_skill = {}
        for skill in job_skills[:5]:  # Limit to first 5 skills
            try:
                resources = fetch_resources(skill)
                resources_by_skill[skill] = resources[:2]  # 2 resources per skill
            except Exception as e:
                logger.warning(f"Failed to fetch resources for skill {skill}: {e}")
                resources_by_skill[skill] = []

        return {
            "job": target_job,
            "skills": job_skills,
            "learning_resources": resources_by_skill
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job skills: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to get job skills: {e}")

