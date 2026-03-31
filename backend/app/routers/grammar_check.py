from fastapi import APIRouter, Body, HTTPException
from app.services.grammar_service import check_grammar
from pydantic import BaseModel

class TextInput(BaseModel):
    text: str

router = APIRouter()

@router.post("/")
def grammar_check(payload: TextInput):
    """
    Receives essay text and returns grammar checking results.
    """
    try:
        result = check_grammar(payload.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Grammar check failed: {str(e)}")
