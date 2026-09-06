from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """This class works as settings and import env files"""

    model_config = SettingsConfigDict(env_file=".env")
    DATABASE_URL: str


settings = Settings()
