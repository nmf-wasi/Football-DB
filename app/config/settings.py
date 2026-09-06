from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """This class works as settings and import env files"""

    model_config = SettingsConfigDict(env_file=".env")
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()
