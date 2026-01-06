from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class InstructorProfile(Base):
    __tablename__ = "instructor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    bio = Column(Text, nullable=True)
    license_category = Column(String, nullable=True) # Ex: "B", "AB"
    hourly_rate = Column(Float, nullable=True) # valor_hora

    # Location
    city = Column(String, index=True, nullable=True) # Added for filtering
    lat = Column(Float, nullable=True)
    long = Column(Float, nullable=True)

    rating = Column(Float, default=0.0)

    user = relationship("User", back_populates="instructor_profile")
