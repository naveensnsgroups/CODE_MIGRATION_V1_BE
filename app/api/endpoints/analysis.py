from fastapi import APIRouter, HTTPException
from app.services.analysis_service import analysis_service

router = APIRouter()

@router.get("/{project_id}/context")
async def get_project_context(project_id: str):
    """
    Fetches the full code context for a project to be analyzed by AI.
    """
    try:
        context = analysis_service.get_project_context(project_id)
        if not context:
            raise HTTPException(status_code=404, detail="No source code found or project empty.")
        
        return {
            "project_id": project_id,
            "context": context,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
