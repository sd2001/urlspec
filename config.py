from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    redis_url: str = Field(..., env="REDIS_URL")  # Required variable
    db_name: str = Field(..., env="DB_NAME")      # Required variable
    url_tablename: str = Field(..., env="URL_TABLENAME")  # Required variable
    running_host: str = Field("localhost", env="RUNNING_HOST")  # Default is "localhost"
    app_port: str = Field(..., env="APP_PORT")  # Default is "localhost"

    class Config:
        env_file = ".env"  # Specify the .env file location


# Instantiate settings
settings = Settings()
