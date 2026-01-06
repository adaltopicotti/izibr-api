from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instrutor"
    STUDENT = "aluno"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True) # Nullable if google auth only
    role = Column(String, default=UserRole.STUDENT.value)
    google_id = Column(String, nullable=True, unique=True)

    instructor_profile = relationship("InstructorProfile", back_populates="user", uselist=False)
    appointments_as_student = relationship("Appointment", back_populates="student", foreign_keys="Appointment.student_id")
    appointments_as_instructor = relationship("Appointment", back_populates="instructor", foreign_keys="Appointment.instructor_id")
