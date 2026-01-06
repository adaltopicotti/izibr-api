import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager

from app.main import app
from app.core.database import get_db, Base
from app.core import security

# Override lifespan to avoid connecting to the production database (dev.db)
# because app/main.py's lifespan tries to create tables in the default engine.
@asynccontextmanager
async def mock_lifespan(app):
    yield
app.router.lifespan_context = mock_lifespan

# Use a FILE database for testing instead of memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_temp.db"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_signup_login(client):
    # Signup
    response = await client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "password123",
        "role": "aluno"
    })
    assert response.status_code == 200, response.text
    assert response.json()["email"] == "test@example.com"

    # Login
    response = await client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200, response.text
    assert "access_token" in response.json()

    token = response.json()["access_token"]

    # Get Me
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_instructor_flow(client):
    # 1. Create Instructor User
    await client.post("/auth/signup", json={
        "email": "instr@example.com",
        "password": "pass",
        "role": "instrutor"
    })

    login_res = await client.post("/auth/login", data={"username": "instr@example.com", "password": "pass"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Profile
    profile_data = {
        "bio": "Expert driver",
        "license_category": "B",
        "hourly_rate": 50.0,
        "city": "Sao Paulo",
        "lat": -23.55,
        "long": -46.63
    }
    response = await client.post("/instructors/", json=profile_data, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["city"] == "Sao Paulo"

    # 3. Search
    response = await client.get("/instructors/?city=Sao Paulo")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["hourly_rate"] == 50.0

    response = await client.get("/instructors/?city=Rio")
    assert response.status_code == 200
    assert len(response.json()) == 0

@pytest.mark.asyncio
async def test_admin_access(client):
    # Create Admin
    await client.post("/auth/signup", json={
        "email": "admin@example.com",
        "password": "pass",
        "role": "admin"
    })
    login_res = await client.post("/auth/login", data={"username": "admin@example.com", "password": "pass"})
    token = login_res.json()["access_token"]

    # Access Admin Dashboard
    response = await client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Create Student
    await client.post("/auth/signup", json={"email": "s@e.com", "password": "p", "role": "aluno"})
    login_res_s = await client.post("/auth/login", data={"username": "s@e.com", "password": "p"})
    token_s = login_res_s.json()["access_token"]

    # Student accessing admin
    response = await client.get("/admin/users", headers={"Authorization": f"Bearer {token_s}"})
    assert response.status_code == 403
