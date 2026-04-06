from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import datetime
import httpx
from app.services.analysis_service import analysis_service
from app.core.config import settings
from app.core.database import db

router = APIRouter()

class SaveReportRequest(BaseModel):
    action: str
    content: str

class ProxyAnalysisRequest(BaseModel):
    full_url: str
    payload: dict

@router.post("/proxy")
async def proxy_analysis(request: ProxyAnalysisRequest):
    """
    Proxies an analysis request to an external agent (e.g. n8n) to bypass CORS.
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(request.full_url, json=request.payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Agent returned error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/reports")
async def get_saved_reports(project_id: str):
    """
    Fetches all saved analysis reports for a specific project from MongoDB.
    """
    try:
        if db.db is None:
            raise HTTPException(status_code=503, detail="Database connection not available")
        
        # Fetch all reports for this project
        cursor = db.db.reports.find({"project_id": project_id})
        reports = []
        for doc in cursor:
            reports.append({
                "action": doc["action"],
                "content": doc["content"],
                "saved_at": doc["saved_at"]
            })
        
        return {"project_id": project_id, "reports": reports, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/save")
async def save_analysis_report(project_id: str, request: SaveReportRequest):
    """
    Saves or updates an AI analysis report in MongoDB.
    """
    try:
        if db.db is None:
            raise HTTPException(status_code=503, detail="Database connection not available")

        report_data = {
            "project_id": project_id,
            "action": request.action,
            "content": request.content,
            "saved_at": datetime.datetime.utcnow().isoformat(),
        }

        # Upsert: Update existing action report or create new one
        result = db.db.reports.update_one(
            {"project_id": project_id, "action": request.action},
            {"$set": report_data},
            upsert=True
        )

        return {
            "status": "saved", 
            "project_id": project_id, 
            "action": request.action,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/context")
async def get_project_context(project_id: str):
    """
    Fetches the full code context for a project to be analyzed by AI.
    """
    try:
        context = analysis_service.get_project_context(project_id)
        if not context:
            raise HTTPException(status_code=404, detail="No source code found or project empty.")
        return {"project_id": project_id, "context": context, "status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

