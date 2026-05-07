from fastapi import FastAPI
from app.routes.job_routes import router as job_router

app = FastAPI() # Initialize the FastAPI application
app.include_router(job_router) # Include the job routes in the application

@app.get("/") # Define a GET endpoint at the root URL
def home():
    return {
        "message": "CareerPilot AI Backend Running"
        } # Return a JSON response indicating that the backend is running   
