from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None)
):
    print(f"Регистрация: {email}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed = get_password_hash(password)
        cursor.execute(
            "INSERT INTO users (email, hashed_password, full_name) VALUES (?, ?, ?)",
            (email, hashed, full_name)
        )
        conn.commit()
        return {"message": "User created successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", (form_data.username,))
        user = cursor.fetchone()
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        access_token = create_access_token(data={"sub": str(user["id"])})
        return {"access_token": access_token, "token_type": "bearer"}