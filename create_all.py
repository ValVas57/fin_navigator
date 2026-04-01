import os

# Создаём папки
os.makedirs("app/routers", exist_ok=True)

# Файл app/database.py
with open("app/database.py", "w", encoding="utf-8") as f:
    f.write("""from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./data/finnavigator.db", connect_args={"check_same_thread": True})
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
    f.write("""from sqlalchemy import Column, Integer, String, Float, Date, DateTime, JSON, ForeignKey
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
    hobbies = Column(JSON)
    family_members = Column(JSON)
    financial_goals = Column(JSON)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0)
    deadline = Column(Date)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""")

# Файл app/auth.py
with open("app/auth.py", "w", encoding="utf-8") as f:
    f.write("""from datetime import datetime, timedelta
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

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, email, password):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(401, "User not found")
    return user
""")

# Файл app/routers/auth.py
with open("app/routers/auth.py", "w", encoding="utf-8") as f:
    f.write("""from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import authenticate_user, create_access_token, get_password_hash
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = None

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    hashed = get_password_hash(user.password)
    new_user = User(email=user.email, password_hash=hashed, full_name=user.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "full_name": current_user.full_name}
""")

# Файл app/routers/profile.py
with open("app/routers/profile.py", "w", encoding="utf-8") as f:
    f.write("""from fastapi import APIRouter, Depends
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
    hobbies: List[str] = []
    family_members: List[dict] = []
    financial_goals: List[str] = []

@router.get("/")
async def get_profile(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        return {"user_id": current_user.id}
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

@router.get("/")
async def get_goals(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Goal).filter(Goal.user_id == current_user.id, Goal.status == "active").all()

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

print("✅ All files created!")
print("")
print("Now run:")
print("pip install sqlalchemy python-jose[cryptography] passlib[bcrypt] bcrypt")
print("python -m uvicorn app.main:app --reload")