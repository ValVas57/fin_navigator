from fastapi import APIRouter, Depends, HTTPException, Form
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])

@router.post("/")
def create_goal(
    name: str = Form(...),
    target_amount: float = Form(...),
    deadline: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO goals (user_id, name, target_amount, deadline)
            VALUES (?, ?, ?, ?)
        """, (current_user["id"], name, target_amount, deadline if deadline else None))
        conn.commit()
        return {"message": "Goal created", "goal_id": cursor.lastrowid}

@router.get("/")
def list_goals(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, target_amount, current_amount, deadline FROM goals WHERE user_id = ?", (current_user["id"],))
        goals = cursor.fetchall()
        return [{"id": g["id"], "name": g["name"], "target_amount": g["target_amount"], "current_amount": g["current_amount"], "deadline": g["deadline"]} for g in goals]