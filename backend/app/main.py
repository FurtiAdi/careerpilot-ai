from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.job_routes import router as job_router

app = FastAPI()

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