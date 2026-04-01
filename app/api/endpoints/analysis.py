from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.analysis_service import analysis_service
from app.core.config import settings
import json
import datetime

router = APIRouter()

class SaveReportRequest(BaseModel):
    action: str
    content: str

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


@router.post("/{project_id}/save")
async def save_analysis_report(project_id: str, request: SaveReportRequest):
    """
    Saves an AI analysis report to disk alongside the project source.
    """
    try:
        project_path = settings.PROJECTS_DIR / project_id
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found.")

        reports_dir = project_path / "reports"
        reports_dir.mkdir(exist_ok=True)

        report_data = {
            "project_id": project_id,
            "action": request.action,
            "content": request.content,
            "saved_at": datetime.datetime.utcnow().isoformat(),
        }

        report_file = reports_dir / f"{request.action}.json"
        report_file.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

        return {"status": "saved", "path": str(report_file)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
