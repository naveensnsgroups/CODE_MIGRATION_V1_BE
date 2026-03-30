import os
from pathlib import Path
from typing import Dict, List, Any

class AnalysisService:
    @staticmethod
    def get_file_tree(project_path: Path) -> List[Dict[str, Any]]:
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
    def detect_metadata(project_path: Path) -> Dict[str, Any]:
        """
        Detects primary language and framework based on entry files.
        """
        metadata = {
            "language": "Unknown",
            "framework": "Unknown",
            "dependencies": []
        }

        # Check for Common Language Files
        if (project_path / "package.json").exists():
            metadata["language"] = "JavaScript/TypeScript"
            metadata["framework"] = "Node.js (likely React/Next.js/Express)"
        elif (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            metadata["language"] = "Python"
            metadata["framework"] = "Django/FastAPI/Flask"
        elif (project_path / "pom.xml").exists() or (project_path / "build.gradle").exists():
            metadata["language"] = "Java"
            metadata["framework"] = "Spring/Maven/Gradle"

        return metadata

analysis_service = AnalysisService()
