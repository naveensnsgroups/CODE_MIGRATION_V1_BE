import shutil
from pathlib import Path
from git import Repo
from app.core.config import settings
import uuid
import hashlib

class CloneService:
    @staticmethod
    def clone_repository(repo_url: str, github_token: str = None) -> str:
        """
        Clones a repository into a unique local storage path.
        Returns the project_id (Deterministic Hash).
        """
        # 🧪 Surgical Deterministic ID
        url_hash = hashlib.sha256(repo_url.lower().strip().encode()).hexdigest()[:12]
        project_id = f"prj_{url_hash}"
        project_path = settings.PROJECTS_DIR / project_id
        
        # 🚀 Shortcut: If project already exists, don't re-clone
        if project_path.exists():
            print(f"[Persistence Hub] Project {project_id} already exists. Resuming session.")
            return project_id
        
        # Ensure directory exists
        project_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Handle Authenticated Git (Safe and Invisible)
            authenticated_url = repo_url
            if github_token and "github.com" in repo_url:
                # Transform https://github.com/org/repo to https://token@github.com/org/repo
                path = repo_url.replace("https://github.com/", "")
                authenticated_url = f"https://{github_token}@github.com/{path}"
                
            # Clone repo
            Repo.clone_from(authenticated_url, project_path)
            return project_id
        except Exception as e:
            # Cleanup on failure
            if project_path.exists():
                shutil.rmtree(project_path)
            raise Exception(f"Failed to clone repository: {str(e)}")

clone_service = CloneService()
