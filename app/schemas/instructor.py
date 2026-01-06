from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserResponse

class InstructorBase(BaseModel):
    bio: Optional[str] = None
    license_category: Optional[str] = None
    hourly_rate: Optional[float] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None

class InstructorCreate(InstructorBase):
    pass

class InstructorUpdate(InstructorBase):
    pass

class InstructorResponse(InstructorBase):
    id: int
    user_id: int
    rating: float
    user: Optional[UserResponse] = None # Include user info if needed

    class Config:
        from_attributes = True
