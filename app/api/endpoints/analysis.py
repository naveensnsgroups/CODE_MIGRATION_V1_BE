from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import datetime
import httpx
from pathlib import Path
from app.services.analysis_service import analysis_service
from app.core.config import settings
from app.core.database import db

router = APIRouter()

# ─── Pydantic Models ─────────────────────────────────────────────────────────

class SaveReportRequest(BaseModel):
    action: str
    content: str

class ProxyAnalysisRequest(BaseModel):
    full_url: str
    payload: dict

# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/{project_id}/reports")
async def get_saved_reports(project_id: str):
    """
    Fetches all saved analysis reports for a specific project from MongoDB.
    Supports both 'reports' and the dedicated 'general_agent' collection.
    """
    try:
        if db.db is None:
            raise HTTPException(status_code=503, detail="Database connection not available")

        # 1. Fetch from standard 'reports' collection (Exclude 'routes' if we want Map Agent priority)
        reports = []
        cursor = db.db.reports.find({"project_id": project_id})
        async for doc in cursor:
            action = doc.get("action", "unknown")
            #  Priority Logic (v26.6): Skip 'routes' here if we expect it from 'map_agent'
            if action == "routes": continue

            doc_id = doc.pop("_id", None)
            reports.append({
                "action": action,
                "content": doc.get("content", doc),
                "saved_at": doc.get("saved_at", datetime.datetime.utcnow().isoformat())
            })

        # 2. Sequential Async Resolution for agent collections
        agent_configs = [
            ("general", db.db.general_agent),
            ("routes", db.db.map_agent),
            ("logic", db.db.logic_agent),
            ("code_layer", db.db.code_analyzer_agent),
            ("migration", db.db.migration_agent),
            ("quick_migration", db.db.standalone_report),
        ]

        for action_name, collection in agent_configs:
            doc = await collection.find_one({"project_id": project_id, "action": action_name})
            if doc:
                doc.pop("_id", None)
                reports.append({
                    "action": action_name,
                    "content": doc.get("content", doc),
                    "saved_at": doc.get("saved_at", datetime.datetime.utcnow().isoformat())
                })

        return {"project_id": project_id, "reports": reports, "status": "success"}
    except Exception as e:
        print(f"[Backend Error] get_saved_reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/proxy")
async def proxy_analysis(request: ProxyAnalysisRequest):
    """
    Proxies an analysis request to an external agent (e.g. n8n) to bypass CORS.
    Surgical 20-minute timeout enabled for heavy logical scans.
    """
    try:
        # Move project_id to end of payload if it exists
        if "project_id" in request.payload:
            pid = request.payload.pop("project_id")
            request.payload["project_id"] = pid

        async with httpx.AsyncClient(timeout=1200.0) as client:
            response = await client.post(request.full_url, json=request.payload)
            response.raise_for_status()
            return response.json()
    except httpx.ReadTimeout:
        # Graceful return for 504 scenarios to allow polling to take over
        return {"status": "mission_started", "message": "Agent is processing in background. Poll for results."}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Agent returned error: {e.response.text}")
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

        #  Surgical Routing (v26.5): 
        # 'general' -> general_agent
        # 'routes' -> map_agent
        # 'logic' -> logic_agent
        # 'code_layer' -> code_analyzer_agent
        # others -> reports
        if request.action == "general":
            target_collection = db.db.general_agent
        elif request.action == "routes":
            target_collection = db.db.map_agent
        elif request.action == "logic":
            target_collection = db.db.logic_agent
        elif request.action == "code_layer":
            target_collection = db.db.code_analyzer_agent
        elif request.action == "migration":
            target_collection = db.db.migration_agent
        elif request.action == "quick_migration":
            target_collection = db.db.standalone_report
        else:
            target_collection = db.db.reports

        result = await target_collection.update_one(
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
    Fetches the full code context for a project and bundles the industrial skill directive.
    """
    try:
        context = await analysis_service.get_project_context(project_id)
        if not context:
            raise HTTPException(status_code=404, detail="No source code found or project empty.")

        skill_content = ""

        return {
            "project_id": project_id,
            "context": context,
            "skill_content": skill_content,
            "status": "success"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills/{action}")
async def get_skill_directive(action: str):
    """
    Fetches a high-depth AI Skill directive from the modular /skills repository.
    """
    try:
        skill_name = action
        skill_file = f"{skill_name}.skill.md"

        skills_dir = Path("e:/CODE_MIGRATION_V1/CODE_MIGRATION_V1_BE/skills")
        skill_path = skills_dir / skill_file

        if not skill_path.exists():
            skill_path = skills_dir / "general.skill.md"

        if not skill_path.exists():
            return {"action": action, "content": "", "status": "no_skill"}

        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {"action": action, "content": content, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
