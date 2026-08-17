from app.database.database import engine
from app.database.database import Base
from app.models.analysis_model import Analysis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.job_routes import router as job_router
from app.routes.analysis_routes import router as analysis_router
from app.routes.auth_routes import router as auth_router
from app.routes.profile_routes import router as profile_router
from app.models.user_model import User
from fastapi.staticfiles import StaticFiles



Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
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


app.include_router(job_router)
app.include_router(analysis_router)
app.include_router(auth_router)
app.include_router(profile_router)