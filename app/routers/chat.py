from fastapi import APIRouter, Depends, Form, HTTPException
from app.auth import get_current_user
from app.services.ai_assistant import process_financial_question, get_education_recommendations

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message")
def chat_message(
    message: str = Form(...)
):
    """AI-чат доступен без авторизации"""
    response = process_financial_question(message, None)
    return {"response": response}

@router.post("/recommendations")
def get_recommendations(
    hobbies: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Образование требует авторизации"""
    hobby_list = [h.strip() for h in hobbies.split(",")] if hobbies else []
    recommendations = get_education_recommendations(hobby_list)
    return {"recommendations": recommendations}