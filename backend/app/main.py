import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routes.analysis_routes import router as analysis_router
from app.routes.auth_routes import router as auth_router
from app.routes.profile_routes import router as profile_router
from app.routes.resume_routes import router as resume_router

from app.routes.tailored_resume_routes import (
    router as tailored_resume_router,
)

logger = logging.getLogger(__name__)

os.makedirs(
    settings.PROFILE_PICTURE_DIR,
    exist_ok=True,
)

app = FastAPI()

app.mount(
    "/uploads/profile_pictures",
    StaticFiles(
        directory=settings.PROFILE_PICTURE_DIR
    ),
    name="profile_pictures",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unexpected application error",
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred."
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins= settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "CareerPilot AI Backend Running"
    }

app.include_router(analysis_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(resume_router)
app.include_router(tailored_resume_router)