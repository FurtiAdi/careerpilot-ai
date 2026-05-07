from fastapi import APIRouter

router = APIRouter()


@router.post("/analyze-job")
def analyze_job():
    return {
        "message": "Job analysis endpoint working"
    }