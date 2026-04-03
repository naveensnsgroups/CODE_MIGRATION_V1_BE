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

class MigrationReportRequest(BaseModel):
    project_id: str
    target_stack: Optional[dict] = None
    roadmap: Optional[list] = None
    feasibility_score: Optional[int] = 0
    modernization_strategy: Optional[str] = None
    summary: Optional[str] = None
    core_features: Optional[list] = None
    business_rules: Optional[list] = None

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
    # 🧪 Extract Owner Username
    url_str = str(request.repo_url).rstrip('/')
    parts = url_str.split('/')
    if len(parts) < 4:
        raise HTTPException(status_code=400, detail="Invalid repository URL.")
    
    owner = parts[3]
    
    # 🔍 Fetch from GitHub API
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
async def receive_migration_report(report: MigrationReportRequest):
    """
    Surgical Modernization Ingestion: Capture n8n transmission and persist to DB.
    """
    from app.core.database import db
    import datetime
    import json

    try:
        if db.db is None:
            raise HTTPException(status_code=503, detail="Database connection not available")

        # 🧪 Construct Industrial Report Payload
        report_data = {
            "project_id": report.project_id,
            "action": "migration",
            "content": json.dumps(report.dict()), # Store as JSON string for consistency
            "saved_at": datetime.datetime.utcnow().isoformat(),
        }

        # 🔍 Upsert Intelligence: Update existing migration report or create new one
        result = db.db.reports.update_one(
            {"project_id": report.project_id, "action": "migration"},
            {"$set": report_data},
            upsert=True
        )

        print(f"[Webhook Ingestion] Surgical Success: Migration intelligence saved for project {report.project_id}")
        
        return {
            "status": "success",
            "project_id": report.project_id,
            "action": "migration"
        }
    except Exception as e:
        print(f"[Webhook Ingestion] ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
