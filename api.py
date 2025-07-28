import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.create_report.main import ReportCreator

load_dotenv()

if not os.getenv("SERPER_API_KEY") or not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("SERPER_API_KEY and/or GROQ_API_KEY are not set.")

class ResearchRequest(BaseModel):
    topic: str
    user_personalization: str | None = None

app = FastAPI(
    title="CrewAI Research API",
    description="An API to trigger a research crew to generate reports.",
    version="1.0.0"
)

@app.get("/", tags=["Status"])
def read_root():
    return {"status": "API is running"}

@app.post("/research", tags=["Research"])
def run_research(request: ResearchRequest):
    try:
        inputs = {
            'topic': request.topic,
            'user_personalization': request.user_personalization
        }
        crew_result = ReportCreator().kickoff(inputs=inputs)
        return {"result": crew_result}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred: {str(e)}"
        )