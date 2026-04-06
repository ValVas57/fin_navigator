from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Profile
class ProfileCreate(BaseModel):
    first_name: Optional[str] = None
    age: Optional[int] = None
    hobbies: Optional[List[str]] = []
    family_size: Optional[int] = 1

class ProfileResponse(ProfileCreate):
    id: int
    user_id: int

# Goals
class GoalCreate(BaseModel):
    name: str
    target_amount: float
    deadline: Optional[date] = None

class GoalResponse(GoalCreate):
    id: int
    user_id: int
    current_amount: float
    created_at: datetime

# Chat
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class RecommendationsRequest(BaseModel):
    hobbies: List[str]

class CourseRecommendation(BaseModel):
    title: str
    description: str
    duration: str
    cost: int
    potential_income: str