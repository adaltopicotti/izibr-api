from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core import security
from app.core.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = security.create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup", response_model=UserResponse)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = User(
        email=user_in.email,
        password_hash=security.get_password_hash(user_in.password),
        role=user_in.role.value,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/login/google")
async def login_google():
    return {"msg": "Redirect to Google OAuth2 URL here"}

@router.get("/callback/google")
async def callback_google(code: str):
    return {"msg": "Process Google OAuth2 callback here", "code": code}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(deps.get_current_user)):
    return current_user
