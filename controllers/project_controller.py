"""
Project controller - business logic for project operations - FIXED
"""

from typing import List
from models.database import DatabaseManager
from models.entities import Project


class ProjectController:
    """Controller for project-related operations"""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_project(self, project: Project) -> int:
        """Create a new project and return its ID"""
        return self.db_manager.create_project(project)

    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        return self.db_manager.get_all_projects()

    def update_project(self, project: Project):
        """Update an existing project"""
        self.db_manager.update_project(project)

    def delete_project(self, project_id: int):
        """Delete a project and all its tasks"""
        self.db_manager.delete_project(project_id)