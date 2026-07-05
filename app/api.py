from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

from app.pipeline import run_research_pipeline

app = FastAPI(title="Multi-Agent Research API")

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Later replace with your React URL
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    topic: str
    sources: list[str]
    report: str
    report_sections: dict[str, Any]
    feedback: str
    feedback_sections: dict[str, Any]
    search_result: str
    reader_result: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/research")
async def research(req: ResearchRequest) -> ResearchResponse:
    try:
        result = await run_in_threadpool(run_research_pipeline, req.topic)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ResearchResponse(
        topic=req.topic,
        sources=result.get("sources", []),
        report=result.get("report", ""),
        report_sections=result.get("report_sections", {}),
        feedback=result.get("feedback", ""),
        feedback_sections=result.get("feedback_sections", {}),
        search_result=result.get("search_result", ""),
        reader_result=result.get("reader_result", ""),
    )