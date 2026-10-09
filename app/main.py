from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for bulk certificate generation.",
    version="1.0.0",
)

app.include_router(api_router, prefix=settings.API_V1_STR)

from app.db.database import engine, Base
from app.models import generation_job, certificate # ensure models are loaded
Base.metadata.create_all(bind=engine)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("static/index.html")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )
