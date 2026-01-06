from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.database import get_db
from app.models.instructor import InstructorProfile
from app.models.user import User
from app.schemas.instructor import InstructorCreate, InstructorUpdate, InstructorResponse

router = APIRouter()

@router.get("/", response_model=List[InstructorResponse])
async def search_instructors(
    city: Optional[str] = Query(None, description="Filter by city"),
    max_price: Optional[float] = Query(None, description="Filter by maximum hourly rate"),
    db: AsyncSession = Depends(get_db)
):
    query = select(InstructorProfile).join(User).options(selectinload(InstructorProfile.user))

    if city:
        query = query.where(InstructorProfile.city == city)
    if max_price:
        query = query.where(InstructorProfile.hourly_rate <= max_price)

    result = await db.execute(query)
    instructors = result.scalars().all()
    return instructors

@router.get("/me", response_model=InstructorResponse)
async def get_my_instructor_profile(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(InstructorProfile).where(InstructorProfile.user_id == current_user.id).options(selectinload(InstructorProfile.user))
    result = await db.execute(query)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.post("/", response_model=InstructorResponse)
async def create_instructor_profile(
    profile_in: InstructorCreate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Ensure user has instructor role (or allow any user to become one?)
    # Spec implies user has a role. Let's enforce it or auto-promote?
    # Spec says User has role field.
    if current_user.role != "instrutor":
         raise HTTPException(status_code=403, detail="Only users with 'instrutor' role can create a profile")

    # Check if exists
    query = select(InstructorProfile).where(InstructorProfile.user_id == current_user.id)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = InstructorProfile(
        user_id=current_user.id,
        **profile_in.model_dump()
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    # We need to refresh/load relationship to return it
    # Easiest way is to fetch it again with options
    result = await db.execute(select(InstructorProfile).where(InstructorProfile.id == profile.id).options(selectinload(InstructorProfile.user)))
    profile = result.scalars().first()
    return profile

@router.put("/me", response_model=InstructorResponse)
async def update_instructor_profile(
    profile_in: InstructorUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(InstructorProfile).where(InstructorProfile.user_id == current_user.id).options(selectinload(InstructorProfile.user))
    result = await db.execute(query)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

@router.get("/{id}", response_model=InstructorResponse)
async def get_instructor_profile(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(InstructorProfile).where(InstructorProfile.id == id).options(selectinload(InstructorProfile.user))
    result = await db.execute(query)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Instructor not found")
    return profile
