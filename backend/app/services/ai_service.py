import os
import json

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_ai_analysis(
    job_description: str,
    candidate_skills: list
):

    prompt = f"""
        You are an AI career assistant.

        Analyze the following job description and candidate skills.

        Return your response ONLY as valid JSON.

        Job Description:
        {job_description}

        Candidate Skills:
        {candidate_skills}

        JSON format:
        {{
        "summary": "short summary",
        "strengths": [
            "strength 1",
            "strength 2"
        ],
        "missing_requirements": [
            "missing skill 1",
            "missing skill 2"
        ],
        "recommendations": [
            "recommendation 1",
            "recommendation 2"
        ]
        }}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_response = response.choices[0].message.content

    parsed_response = json.loads(ai_response)

    return parsed_response