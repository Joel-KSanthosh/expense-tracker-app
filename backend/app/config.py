from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Jwt(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_expire_minutes: int = 30
    refresh_expire_days: int = 7

    model_config = SettingsConfigDict(env_prefix="JWT_", use_enum_values=True)


class Postgres(BaseSettings):
    host: str
    port: int
    user: str
    password_secret_name: str
    db: str

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", use_enum_values=True)


class Settings(BaseSettings):
    postgres: Postgres = Postgres()  # pyright: ignore[reportCallIssue]
    jwt: Jwt = Jwt()  # pyright: ignore[reportCallIssue]

    model_config = SettingsConfigDict(env_file=".env", use_enum_values=True, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
