from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.services.clone_service import clone_service
from app.services.analysis_service import analysis_service
from app.core.config import settings

router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: HttpUrl
    github_token: Optional[str] = None

@router.post("/")
async def ingest_repository(request: IngestRequest):
    """
    Ingest a repository from GitHub.
    1. Clone repo locally.
    2. Analyze structure.
    3. Detect metadata.
    """
    try:
        project_id = clone_service.clone_repository(str(request.repo_url), request.github_token)
        project_path = settings.PROJECTS_DIR / project_id
        
        # Analyze Project
        file_tree = analysis_service.get_file_tree(project_path)
        metadata = analysis_service.detect_metadata(project_path)
        
        # Extract Project Name from URL
        project_name = str(request.repo_url).rstrip('/').split('/')[-1].replace('.git', '')
        
        return {
            "project_id": project_id,
            "project_name": project_name,
            "metadata": metadata,
            "file_tree": file_tree,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
