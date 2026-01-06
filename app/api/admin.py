from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(deps.get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    return result.scalars().all()
