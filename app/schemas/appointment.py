from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.appointment import AppointmentStatus

class AppointmentBase(BaseModel):
    instructor_id: int
    date_time: datetime

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    status: AppointmentStatus

class AppointmentResponse(AppointmentBase):
    id: int
    student_id: int
    status: str

    class Config:
        from_attributes = True
