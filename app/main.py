from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api import auth, instructors, appointments, admin
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(instructors.router, prefix="/instructors", tags=["instructors"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Instructor Platform API"}
