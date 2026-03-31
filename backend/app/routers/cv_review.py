from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.cv_service import parse_resume

router = APIRouter()

@router.post("/")
async def review_cv(file: UploadFile = File(...)):
    """
    Endpoint to accept resume upload and return parsing info.
    """
    try:
        contents = await file.read()
        result = parse_resume(contents, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
