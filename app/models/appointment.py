from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime

class AppointmentStatus(str, enum.Enum):
    PENDING = "pendente"
    CONFIRMED = "confirmado"
    COMPLETED = "concluido"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    date_time = Column(DateTime, nullable=False)
    status = Column(String, default=AppointmentStatus.PENDING.value)

    student = relationship("User", foreign_keys=[student_id], back_populates="appointments_as_student")
    instructor = relationship("User", foreign_keys=[instructor_id], back_populates="appointments_as_instructor")
