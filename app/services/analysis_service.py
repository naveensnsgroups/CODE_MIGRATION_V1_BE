import os
from pathlib import Path
from typing import Dict, List, Any

class AnalysisService:
    @staticmethod
    async def get_file_tree(project_path: Path) -> List[Dict[str, Any]]:
        """
        Generates a recursive file tree structure for the project.
        """
        def build_tree(current_path: Path) -> List[Dict[str, Any]]:
            tree = []
            for item in sorted(current_path.iterdir()):
                # Skip hidden files/directories (optional)
                if item.name.startswith('.'):
                    continue
                
                node = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                }
                
                if item.is_dir():
                    node["children"] = build_tree(item)
                
                tree.append(node)
            return tree

        return build_tree(project_path)

    @staticmethod
    async def detect_metadata(project_path: Path) -> Dict[str, Any]:
        """
        Detects primary language and framework based on entry files.
        """
        metadata = {
            "language": "Unknown",
            "framework": "Unknown",
            "dependencies": []
        }

        # 1. Check for Manifests (package.json, etc.)
        if (project_path / "package.json").exists():
            metadata["language"] = "Javascript/Typescript"
            metadata["framework"] = "Node.js (NPM)"
        elif (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            metadata["language"] = "Python"
            metadata["framework"] = "Flask/FastAPI/Django"
        
        # 2. Legacy/Markdown Detection (Protocol #5)
        cobol_files = list(project_path.glob("**/*.cob")) + list(project_path.glob("**/*.cbl"))
        sql_files = list(project_path.glob("**/*.sql"))
        md_files = list(project_path.glob("**/*.md"))

        if not metadata["language"] != "Unknown":
            if cobol_files:
                metadata["language"] = "COBOL (Legacy)"
                metadata["framework"] = "Mainframe System"
            elif sql_files and len(sql_files) > len(list(project_path.glob("**/*.js"))):
                metadata["language"] = "SQL"
                metadata["framework"] = "Database Schema"
            elif md_files and not list(project_path.glob("**/*.py")):
                metadata["language"] = "Technical Docs"
                metadata["framework"] = "Markdown Suite"
            elif list(project_path.glob("**/*.html")):
                metadata["language"] = "Vanilla Web (HTML/CSS/JS)"
                metadata["framework"] = "Static Website"

        return metadata

    @staticmethod
    async def get_project_context(project_id: str) -> List[Dict[str, str]]:
        """
        Gathers all source code from the project for LLM analysis.
        Returns a list of {"file_name": str, "content": str} objects.
        """
        from app.core.config import settings
        project_path = settings.PROJECTS_DIR / project_id
        context = []
        
        # Files to include (source code & sensitive context)
        valid_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.json',
            '.md', '.txt', '.sql', '.cob', '.cbl', '.f90', '.f',
            '.yaml', '.yml', '.env'
        }
        ignored_dirs = {'node_modules', 'venv', '.git', '__pycache__', 'dist', 'build'}

        for root, dirs, files in os.walk(project_path):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in valid_extensions:
                    try:
                        relative_path = str(file_path.relative_to(project_path))
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            context.append({
                                "file_name": relative_path,
                                "content": content
                            })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        return context

analysis_service = AnalysisService()
