from fastapi import FastAPI, Depends
from app.services.db_services import get_db
from sqlalchemy.orm import Session
from app.config import settings
from typing import List


def create_app() -> FastAPI:
    app = FastAPI(debug=settings.FASTAPI_DEBUG)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    return app