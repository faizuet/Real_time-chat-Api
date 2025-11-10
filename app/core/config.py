from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # ---------- Database ----------
    DATABASE_URI: str = Field(..., env="DATABASE_URI")  # Field name matches .env key

    # ---------- JWT Configuration ----------
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate settings
settings = Settings()

