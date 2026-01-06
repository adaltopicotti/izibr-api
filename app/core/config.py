from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Instructor Platform"
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    SECRET_KEY: str = "CHANGE_ME_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OAuth2 Google (Placeholders)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
