from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from app.services.resource_service import fetch_resources

router = APIRouter()

@router.get("/")
def get_resources(skill: str = Query(..., min_length=2)):
    """
    Returns learning resources based on the requested skill.
    """
    try:
        resources = fetch_resources(skill)
        return {
            "skill": skill,
            "resources": resources,
            "total_resources": len(resources)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch resources: {str(e)}")

@router.get("/bulk")
def get_bulk_resources(skills: str = Query(..., description="Comma-separated list of skills")):
    """
    Returns learning resources for multiple skills.
    """
    try:
        skill_list = [skill.strip() for skill in skills.split(",") if skill.strip()]

        if len(skill_list) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 skills allowed")

        resources_by_skill = {}
        for skill in skill_list:
            try:
                resources = fetch_resources(skill)
                resources_by_skill[skill] = resources[:3]  # Limit to 3 resources per skill
            except Exception as e:
                resources_by_skill[skill] = []

        return {
            "skills": skill_list,
            "resources": resources_by_skill,
            "total_skills": len(skill_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch bulk resources: {str(e)}")

@router.get("/trending")
def get_trending_skills():
    """
    Returns trending skills and their learning resources.
    """
    try:
        # Define trending skills in tech
        trending_skills = [
            "artificial intelligence",
            "machine learning", 
            "react",
            "python",
            "kubernetes",
            "cloud computing",
            "typescript",
            "devops",
            "cybersecurity",
            "data science"
        ]

        trending_resources = {}
        for skill in trending_skills[:5]:  # Limit to top 5
            try:
                resources = fetch_resources(skill)
                trending_resources[skill] = resources[:2]  # 2 resources per skill
            except Exception as e:
                trending_resources[skill] = []

        return {
            "trending_skills": trending_skills,
            "resources": trending_resources,
            "message": "Top trending skills in tech with learning resources"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch trending resources: {str(e)}")
