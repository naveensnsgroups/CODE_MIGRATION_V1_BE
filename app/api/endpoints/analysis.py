from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.analysis_service import analysis_service
from app.core.config import settings
from app.core.database import db
import datetime

router = APIRouter()

class SaveReportRequest(BaseModel):
    action: str
    content: str

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

