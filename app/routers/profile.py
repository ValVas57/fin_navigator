from fastapi import APIRouter, Depends
import json
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/")
def get_profile(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (current_user["id"],))
        profile = cursor.fetchone()
        
        if not profile:
            cursor.execute(
                "INSERT INTO profiles (user_id, hobbies, family_size) VALUES (?, ?, ?)",
                (current_user["id"], "[]", 1)
            )
            conn.commit()
            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (current_user["id"],))
            profile = cursor.fetchone()
        
        return {
            "first_name": profile["first_name"],
            "age": profile["age"],
            "hobbies": json.loads(profile["hobbies"]) if profile["hobbies"] else [],
            "family_size": profile["family_size"] or 1
        }

@router.post("/")
def update_profile(
    first_name: str = None,
    age: int = None,
    hobbies: str = None,
    family_size: int = 1,
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM profiles WHERE user_id = ?", (current_user["id"],))
        exists = cursor.fetchone()
        
        hobbies_json = hobbies if hobbies else "[]"
        
        if exists:
            cursor.execute("""
                UPDATE profiles 
                SET first_name = ?, age = ?, hobbies = ?, family_size = ?
                WHERE user_id = ?
            """, (first_name, age, hobbies_json, family_size, current_user["id"]))
        else:
            cursor.execute("""
                INSERT INTO profiles (user_id, first_name, age, hobbies, family_size)
                VALUES (?, ?, ?, ?, ?)
            """, (current_user["id"], first_name, age, hobbies_json, family_size))
        
        conn.commit()
        return {"message": "Profile updated"}