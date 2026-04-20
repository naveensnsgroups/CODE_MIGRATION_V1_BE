from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.services.clone_service import clone_service
from app.services.analysis_service import analysis_service
from app.core.config import settings

from app.services.email_service import email_service

router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: HttpUrl
    github_token: Optional[str] = None

class ResolveOwnerRequest(BaseModel):
    repo_url: HttpUrl

class AccessRequest(BaseModel):
    repo_url: HttpUrl
    owner_email: str
    request_user: str

class IntelligenceRequest(BaseModel):
    project_id: str
    action: str
    content: Optional[str] = None
    # Support legacy flat fields if necessary
    summary: Optional[str] = None

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
        if "PRIVATE_REPOSITORY_ACCESS_DENIED" in str(e):
            raise HTTPException(status_code=403, detail="PRIVATE_REPOSITORY")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resolve-owner")
async def resolve_owner(request: ResolveOwnerRequest):
    """
    Surgical Owner Resolution: Profile fetch + Commit Intelligence Fallback.
    """
    #  Extract Owner Username
    url_str = str(request.repo_url).rstrip('/')
    parts = url_str.split('/')
    if len(parts) < 4:
        raise HTTPException(status_code=400, detail="Invalid repository URL.")
    
    owner = parts[3]
    
    #  Fetch from GitHub API
    import httpx
    async with httpx.AsyncClient() as client:
        try:
            # Phase 1: Profile Resolution
            profile_response = await client.get(f"https://api.github.com/users/{owner}", timeout=5.0)
            email = None
            if profile_response.status_code == 200:
                email = profile_response.json().get("email")
            
            # Phase 2: Commit Intelligence Fallback (If profile email is null)
            if not email:
                print(f"[Owner Resolution] Profile email hidden. Mining commit history for @{owner}...")
                events_response = await client.get(f"https://api.github.com/users/{owner}/events/public", timeout=5.0)
                if events_response.status_code == 200:
                    events = events_response.json()
                    for event in events:
                        if event.get("type") == "PushEvent":
                            commits = event.get("payload", {}).get("commits", [])
                            for commit in commits:
                                author_email = commit.get("author", {}).get("email")
                                if author_email and "noreply.github.com" not in author_email:
                                    email = author_email
                                    print(f"[Owner Resolution] Intelligence Success (Phase 2): Found email {email}")
                                    break
                        if email: break

            # Phase 3: Nuclear Fallback - Scan Recent Public Repo Commits
            if not email:
                print(f"[Owner Resolution] Phase 2 failed. Performing Phase 3 Nuclear Repo Scan for @{owner}...")
                repos_response = await client.get(f"https://api.github.com/users/{owner}/repos?sort=updated&per_page=5", timeout=5.0)
                if repos_response.status_code == 200:
                    repos = repos_response.json()
                    for repo in repos:
                        repo_name = repo.get("name")
                        commits_response = await client.get(f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=1", timeout=5.0)
                        if commits_response.status_code == 200:
                            commit_data = commits_response.json()
                            if commit_data and isinstance(commit_data, list):
                                author_email = commit_data[0].get("commit", {}).get("author", {}).get("email")
                                if author_email and "noreply.github.com" not in author_email:
                                    email = author_email
                                    print(f"[Owner Resolution] Intelligence Success (Phase 3): Found email {email} in repo {repo_name}")
                                    break
                        if email: break
            
            return {
                "owner_username": owner,
                "owner_email": email
            }
        except Exception as e:
            print(f"[Owner Resolution] Error fetching profile: {str(e)}")
            return {"owner_username": owner, "owner_email": None}

@router.post("/request-access")
async def request_access(request: AccessRequest):
    """
    Automated Outreach: Send email to repository owner.
    """
    success = email_service.send_access_request_email(
        owner_email=request.owner_email,
        repo_url=str(request.repo_url),
        request_user=request.request_user
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send access request email.")
        
    return {"status": "success", "message": "Access request sent successfully."}

@router.post("/migration")
@router.post("/intelligence")
async def receive_intelligence(report: IntelligenceRequest):
    """
    Surgical Intelligence Ingestion: Capture any  mission segment and persist to DB.
    """
    from app.core.database import db
    import datetime
    import json

    try:
        if db.db is None:
            raise HTTPException(status_code=503, detail="Database connection not available")

        #  Dynamic Payload Alignment: Handle both raw 'content' and flat fields
        payload = {}
        if report.content:
            try:
                payload = json.loads(report.content)
            except:
                payload = {"data": report.content}
        else:
            # Fallback to flat fields
            payload = report.dict(exclude_none=True)

        report_data = {
            "project_id": report.project_id,
            "action": report.action,
            "content": json.dumps(payload),
            "saved_at": datetime.datetime.utcnow().isoformat(),
        }

        #  Upsert Intelligence: Update existing report for this action or create new one
        result = db.db.reports.update_one(
            {"project_id": report.project_id, "action": report.action},
            {"$set": report_data},
            upsert=True
        )

        print(f"[Intelligence Ingestion] Surgical Success: '{report.action}' saved for project {report.project_id}")
        
        return {
            "status": "success",
            "project_id": report.project_id,
            "action": report.action
        }
    except Exception as e:
        print(f"[Intelligence Ingestion] ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
async def get_project_ingestion(project_id: str):
    """
    Surgical Metadata Port: Retrieve file tree, metadata, and modernization intelligence.
    """
    from app.core.database import db
    import json

    project_path = settings.PROJECTS_DIR / project_id
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found.")
        
    try:
        # Phase 1: Re-Analyze/Fetch Project Structure
        file_tree = analysis_service.get_file_tree(project_path)
        metadata = analysis_service.detect_metadata(project_path)
        project_name = project_id.replace('prj_', '').split('_')[0] 

        # Phase 2: Modernization Intelligence Port (Sync from DB)
        reports = {}
        if db.db is not None:
            cursor = db.db.reports.find({"project_id": project_id})
            for report in cursor:
                action = report.get("action")
                content = report.get("content")
                if action and content:
                    try:
                        reports[action] = json.loads(content)
                    except:
                        reports[action] = content

        return {
            "project_id": project_id,
            "project_name": project_name,
            "metadata": metadata,
            "file_tree": file_tree,
            "reports": reports,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/file")
async def get_file_content(project_id: str, path: str):
    """
    Surgical File Retrieval: Securely read and return file contents for auditing.
    """
    import os
    
    #  Absolute Path Boundary: Ensure project exists
    project_path = settings.PROJECTS_DIR / project_id
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found.")
    
    #  Security Protocol: Prevent directory traversal (../)
    file_path = (project_path / path).resolve()
    if not str(file_path).startswith(str(project_path.resolve())):
        raise HTTPException(status_code=403, detail="Security Violation: Access denied.")
    
    #  Existence Check: Ensure it's a file
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
        
    try:
        import mimetypes
        import base64
        
        mime_type, _ = mimetypes.guess_type(file_path)
        is_image = mime_type and mime_type.startswith("image/")
        
        if is_image:
            with open(file_path, "rb") as f:
                binary_content = f.read()
                base64_content = base64.b64encode(binary_content).decode("utf-8")
            return {
                "project_id": project_id,
                "path": path,
                "content": base64_content,
                "mime_type": mime_type,
                "type": "image",
                "status": "success"
            }
        
        #  Text Protocol: Standard UTF-8 read
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "project_id": project_id,
            "path": path,
            "content": content,
            "type": "text",
            "status": "success"
        }
    except UnicodeDecodeError:
        #  Binary Guard: If text read fails, mark as binary
        return {
            "project_id": project_id,
            "path": path,
            "type": "binary",
            "status": "success",
            "detail": "Binary asset detected. Visual rendering required."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
