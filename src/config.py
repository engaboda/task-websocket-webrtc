import logging
import redis
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import Field
from dotenv import load_dotenv

is_dotenv_loaded = load_dotenv('src/.env')
logger = logging.getLogger(__name__)
logger.info(f'is_dotenv_loaded: {is_dotenv_loaded}')


class DatabaseConfig(BaseSettings):
    """Database configuration settings"""
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # Postgresql specific settings
    postgres_host: str = Field(default="host.docker.internal", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="zakaa_user", env="POSTGRES_USER")
    postgres_password: str = Field(default="zakaa_pass", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="rwaj_db", env="POSTGRES_DB")

    @property
    def postgres_url(self) -> str:
        """Generate Postgresql URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


class FastAPIConfig(BaseSettings):
    """FastAPI configuration settings"""
    host: str = Field(default="0.0.0.0", env="FASTAPI_HOST")
    port: int = Field(default=8000, env="FASTAPI_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="info", env="LOG_LEVEL")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    MAIN_PREFIX: str = Field(
        default="/api",
        env='MAIN_PREFIX'
    )
    LOG_FILE_PATH: str = Field(
        default=r'D:\RWAJ\logs\rwaj.log',
        env='LOG_FILE_PATH'
    )


class RedisConfig(BaseSettings):
    """Redis configuration settings for caching (optional)"""
    url: Optional[str] = Field(default="redis://redis:6379/0", env="REDIS_URL")
    host: Optional[str] = Field(default='redis', env='REDIS_HOSTNAME')
    port: Optional[str] = Field(default='6379', env='REDIS_PORT')
    db: Optional[str] = Field(default='0', env='REDIS_DB')

    @property
    def redis_client(self):
        return redis.Redis(host=self.host, port=self.port, db=self.db)


class LiveKitConfig(BaseSettings):
    url: str = Field(default="wss://gotry-8fsnin9o.livekit.cloud", env='LIVEKIT_WS_URL')
    api_key: str = Field(default='API7vK4jxz9TSBX', env='LIVEKIT_API_KEY')
    secret_key: str = Field(default='Wx2OG9LvONllcw6DRVotM29dZ3s7aFkoUZvUJJKa7CL', env='LIVEKIT_API_SECRET')


class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = Field(default="RWAJ", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")

    database: DatabaseConfig = DatabaseConfig()
    fastapi: FastAPIConfig = FastAPIConfig()
    redis: RedisConfig = RedisConfig()
    livekit: LiveKitConfig = LiveKitConfig()


# Create global settings instance
settings = Settings()
