from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.api import deps
from app.core.database import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate

router = APIRouter()

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_in: AppointmentCreate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Determine student (current user) and instructor
    if current_user.role == "instrutor":
         raise HTTPException(status_code=400, detail="Instructors cannot book appointments as students")

    # Verify instructor exists (optional, FK constraint will catch it but nicer to have check)
    # Using FK constraint logic for now to keep it simple or check `appointment_in.instructor_id`

    appointment = Appointment(
        student_id=current_user.id,
        instructor_id=appointment_in.instructor_id,
        date_time=appointment_in.date_time,
        status=AppointmentStatus.PENDING.value
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment

@router.get("/me", response_model=List[AppointmentResponse])
async def get_my_appointments(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == "aluno":
        query = select(Appointment).where(Appointment.student_id == current_user.id)
    elif current_user.role == "instrutor":
        query = select(Appointment).where(Appointment.instructor_id == current_user.id)
    else: # Admin
        query = select(Appointment) # Admin sees all? Or restrict? Let's assume admin sees all via admin panel, here maybe just theirs if any.
        # Actually admin shouldn't be booking usually.
        query = select(Appointment).where(Appointment.student_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().all()

@router.put("/{id}", response_model=AppointmentResponse)
async def update_appointment_status(
    id: int,
    status_update: AppointmentUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Appointment).where(Appointment.id == id)
    result = await db.execute(query)
    appointment = result.scalars().first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Permission check
    # Student can cancel (maybe?)
    # Instructor can confirm/complete
    if current_user.role == "instrutor":
        if appointment.instructor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your appointment")
    elif current_user.role == "aluno":
        # Maybe allow cancel only?
        if appointment.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your appointment")
        # For simplicity, allowing update if valid, but typically restricted

    appointment.status = status_update.status
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment
