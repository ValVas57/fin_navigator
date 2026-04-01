import os

# Создаём папки
os.makedirs("app/services", exist_ok=True)
os.makedirs("app/routers", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Файл app/__init__.py
with open("app/__init__.py", "w", encoding="utf-8") as f:
    f.write("# FinNavigator - AI assistant for personal finance\n")

# Файл app/config.py
with open("app/config.py", "w", encoding="utf-8") as f:
    f.write("""from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()
""")

# Файл app/database.py
with open("app/database.py", "w", encoding="utf-8") as f:
    f.write("""from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    "sqlite:///./data/finnavigator.db",
    connect_args={"check_same_thread": True}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

# Файл app/models.py
with open("app/models.py", "w", encoding="utf-8") as f:
    f.write("""from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    first_name = Column(String(100))
    age = Column(Integer)
    occupation = Column(String(255))
    hobbies = Column(JSON)
    family_members = Column(JSON)
    financial_goals = Column(JSON)
    risk_tolerance = Column(String(20))
    profile_completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0)
    deadline = Column(Date)
    priority = Column(Integer, default=1)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""")

# Файл app/main.py
with open("app/main.py", "w", encoding="utf-8") as f:
    f.write("""from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.database import engine, Base
from app.routers import auth, profile, goals

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinNavigator")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(goals.router)

# Static files
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return {"message": "FinNavigator is running!", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}
""")

# Файл app/auth.py
with open("app/auth.py", "w", encoding="utf-8") as f:
    f.write("""from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
""")

# Файл app/routers/__init__.py
with open("app/routers/__init__.py", "w", encoding="utf-8") as f:
    f.write("")

# Файл app/routers/auth.py
with open("app/routers/auth.py", "w", encoding="utf-8") as f:
    f.write("""from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = None

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    hashed = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, password_hash=hashed, full_name=user_data.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "full_name": new_user.full_name}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "full_name": current_user.full_name}
""")

# Файл app/routers/profile.py
with open("app/routers/profile.py", "w", encoding="utf-8") as f:
    f.write("""from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserProfile
from app.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/profile", tags=["profile"])

class ProfileCreate(BaseModel):
    first_name: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    hobbies: List[str] = []
    family_members: List[dict] = []
    financial_goals: List[str] = []

@router.get("/")
async def get_profile(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        return {"user_id": current_user.id, "first_name": None, "age": None, "hobbies": [], "family_members": [], "financial_goals": []}
    return profile

@router.post("/")
async def create_or_update_profile(data: ProfileCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        for key, value in data.dict().items():
            setattr(profile, key, value)
    else:
        profile = UserProfile(user_id=current_user.id, **data.dict())
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
""")

# Файл app/routers/goals.py
with open("app/routers/goals.py", "w", encoding="utf-8") as f:
    f.write("""from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import Goal
from app.auth import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/goals", tags=["goals"])

class GoalCreate(BaseModel):
    name: str
    target_amount: float
    deadline: Optional[date] = None
    priority: int = 1

@router.get("/")
async def get_goals(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.query(Goal).filter(Goal.user_id == current_user.id, Goal.status == "active").all()
    return goals

@router.post("/")
async def create_goal(data: GoalCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    new_goal = Goal(user_id=current_user.id, **data.dict())
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

@router.post("/{goal_id}/contribute")
async def contribute(goal_id: int, amount: float, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(404, "Goal not found")
    goal.current_amount += amount
    if goal.current_amount >= goal.target_amount:
        goal.status = "achieved"
    db.commit()
    return {"current_amount": goal.current_amount, "remaining": goal.target_amount - goal.current_amount}
""")

# Файл static/index.html
with open("static/index.html", "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinNavigator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; background: #f5f0e8; color: #2c2c2c; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #c47a5e; margin-bottom: 20px; }
        .status { background: #e8e0d5; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
        .btn { background: #c47a5e; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
        .btn:hover { background: #a55e42; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FinNavigator</h1>
        <div class="status">
            <p>Server is running!</p>
            <p>Your AI assistant for personal finance.</p>
        </div>
        <button class="btn" onclick="checkHealth()">Check Server</button>
        <p id="result" style="margin-top: 20px;"></p>
    </div>
    <script>
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                document.getElementById('result').innerHTML = 'Server response: ' + JSON.stringify(data);
            } catch(e) {
                document.getElementById('result').innerHTML = 'Error: ' + e.message;
            }
        }
    </script>
</body>
</html>
""")

print("All files created successfully!")
print("")
print("Now run:")
print("pip install fastapi uvicorn sqlalchemy python-dotenv python-jose[cryptography] passlib[bcrypt] bcrypt")
print("python -m uvicorn app.main:app --reload")
print("")
print("Then open browser: http://localhost:8000")