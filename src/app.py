from logging.config import dictConfig

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .config import settings
from .routes import rwaj_routers


def setup_logger():
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s: %(levelname)s {%(filename)s:%(lineno)d} -> %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": settings.fastapi.LOG_FILE_PATH,
                "formatter": "default",
                "encoding": "utf-8",  # 👈 ensures UTF-8 encoding
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
    }
    dictConfig(LOGGING_CONFIG)


setup_logger()


def create_app():
    api = FastAPI(root_path=settings.fastapi.MAIN_PREFIX)

    # CORS config
    api.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.fastapi.cors_origins],  # or restrict to specific domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_logger()

    api.include_router(rwaj_routers)

    return api


app = create_app()