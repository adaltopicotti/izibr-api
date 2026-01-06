from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.STUDENT

class UserResponse(UserBase):
    id: int
    role: str
    google_id: Optional[str] = None

    class Config:
        from_attributes = True
