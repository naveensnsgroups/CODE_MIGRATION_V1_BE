import shutil
from pathlib import Path
from git import Repo
from app.core.config import settings
import uuid

class CloneService:
    @staticmethod
    def clone_repository(repo_url: str) -> str:
        """
        Clones a repository into a unique local storage path.
        Returns the project_id.
        """
        project_id = str(uuid.uuid4())
        project_path = settings.PROJECTS_DIR / project_id
        
        # Ensure directory exists
        project_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Clone repo
            Repo.clone_from(repo_url, project_path)
            return project_id
        except Exception as e:
            # Cleanup on failure
            if project_path.exists():
                shutil.rmtree(project_path)
            raise Exception(f"Failed to clone repository: {str(e)}")

clone_service = CloneService()
