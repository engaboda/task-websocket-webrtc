from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from src.config import settings
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def get_session() -> tuple[async_sessionmaker, AsyncEngine]:
    """Create async session for Postgresql database"""
    # Use Postgresql URL if available, otherwise fallback to default
    db_url = settings.database.postgres_url

    engine = create_async_engine(
        db_url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        future=True
    )

    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
    ), engine


RwajSession, RwajEngine = get_session()
