import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database.database import engine
from app.database.database import Base
from app.models.analysis_model import Analysis
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analysis_routes import router as analysis_router
from app.routes.auth_routes import router as auth_router
from app.routes.profile_routes import router as profile_router
from app.routes.resume_routes import router as resume_router
from app.models.user_model import User

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI()

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
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
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