"""
Enhanced Task controller - business logic for task operations with bug tracking features
Extends original TaskController with enhanced functionality for Money Mentor AI
"""
import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from models.database import DatabaseManager
from models.entities import (
    Task, TaskStatus, Comment, User, Module, Version, Label,
    SearchFilter, DashboardMetrics, Attachment, Notification
)


class TaskController:
    """Enhanced controller for task-related operations with bug tracking features"""

    def __init__(self):
        self.db_manager = DatabaseManager()

    # ==================== ORIGINAL METHODS (Enhanced) ====================

    def create_task(self, task: Task) -> int:
        """Create a new task with enhanced bug tracking features"""
        # Validate task data
        self._validate_task_data(task)

        # Create task in database
        task_id = self.db_manager.create_task(task)

        # Send notifications
        self._notify_task_created(task_id, task)

        return task_id

    def get_tasks_by_project(self, project_id: Optional[int] = None) -> List[Task]:
        """Get tasks by project (simplified interface for backward compatibility)"""
        search_filter = SearchFilter(project_id=project_id)
        return self.db_manager.get_enhanced_tasks_by_filter(search_filter)

    def update_task(self, task: Task):
        """Update an existing task with change tracking"""
        if not task.id:
            raise ValueError("Task ID is required for updates")

        # Get original task for comparison
        original_task = self.get_task_by_id(task.id)
        if not original_task:
            raise ValueError(f"Task with ID {task.id} not found")

        # Validate updated data
        self._validate_task_data(task)

        # Update task in database
        self.db_manager.update_task(task)

        # Track changes and send notifications
        self._track_task_changes(original_task, task)

        # Update timestamp
        task.updated_at = datetime.now()

    def update_task_status(self, task_id: int, new_status_id: int, changed_by: Optional[int] = None):
        """Update task status and record history with user tracking"""
        self.db_manager.update_task_status(task_id, new_status_id)

        # Send status change notification
        if changed_by:
            self._notify_status_change(task_id, new_status_id, changed_by)

    def delete_task(self, task_id: int):
        """Delete a task with proper cleanup"""
        # Get task info before deletion
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Delete from database (cascades to related records)
        self.db_manager.delete_task(task_id)

        # Log deletion
        print(f"🗑️ Task deleted: {task.title} (#{task.id})")

    def get_all_statuses(self) -> List[TaskStatus]:
        """Get all task statuses"""
        return self.db_manager.get_all_statuses()

    def add_comment(self, task_id: int, content: str, author_id: Optional[int] = None) -> int:
        """Add a comment to a task with author tracking"""
        comment = Comment(
            id=None,
            task_id=task_id,
            content=content,
            author_id=author_id
        )
        comment_id = self.db_manager.add_comment(comment)

        # Send comment notification
        if author_id:
            self._notify_comment_added(task_id, comment_id, author_id)

        return comment_id

    def get_task_comments(self, task_id: int) -> List[Comment]:
        """Get all comments for a task"""
        return self.db_manager.get_task_comments(task_id)

    def get_project_statistics(self, project_id: Optional[int] = None) -> dict:
        """Get task statistics by status (simplified for backward compatibility)"""
        metrics = self.db_manager.get_dashboard_metrics()
        return metrics.issues_by_status

    def search_tasks(self, query: str, project_id: Optional[int] = None) -> List[Task]:
        """Search tasks by title or description (simplified interface)"""
        search_filter = SearchFilter(query=query, project_id=project_id)
        return self.db_manager.get_enhanced_tasks_by_filter(search_filter)

    # ==================== NEW ENHANCED METHODS ====================

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a single task by ID with all related data"""
        search_filter = SearchFilter()
        tasks = self.db_manager.get_enhanced_tasks_by_filter(search_filter)
        return next((task for task in tasks if task.id == task_id), None)

    def search_tasks_advanced(self, search_filter: SearchFilter) -> List[Task]:
        """Advanced task search with multiple filters"""
        return self.db_manager.get_enhanced_tasks_by_filter(search_filter)

    def get_dashboard_metrics(self, user_id: Optional[int] = None) -> DashboardMetrics:
        """Get comprehensive dashboard metrics"""
        return self.db_manager.get_dashboard_metrics(user_id)

    def get_my_assigned_tasks(self, user_id: int, status_filter: Optional[str] = None) -> List[Task]:
        """Get tasks assigned to specific user"""
        search_filter = SearchFilter(assignee_id=user_id)

        if status_filter == "open":
            # Filter for open statuses
            search_filter.status_id = None  # Will be handled in query

        return self.db_manager.get_enhanced_tasks_by_filter(search_filter)

    def get_tasks_by_module(self, module_id: int) -> List[Task]:
        """Get all tasks for a specific module"""
        search_filter = SearchFilter(module_id=module_id)
        return self.db_manager.get_enhanced_tasks_by_filter(search_filter)

    def get_critical_bugs(self) -> List[Task]:
        """Get all critical priority bugs"""
        search_filter = SearchFilter(issue_type="BUG", priority=1)  # Critical
        return self.db_manager.get_enhanced_tasks_by_filter(search_filter)

    def get_recent_activity(self, days: int = 7, limit: int = 20) -> List[Task]:
        """Get recently updated tasks"""
        from_date = datetime.now() - timedelta(days=days)
        search_filter = SearchFilter(updated_from=from_date)
        tasks = self.db_manager.get_enhanced_tasks_by_filter(search_filter)
        return tasks[:limit]

    # ==================== LABEL MANAGEMENT ====================

    def get_all_labels(self) -> List[Label]:
        """Get all available labels"""
        return self.db_manager.get_all_labels()

    def create_label(self, name: str, color: str, description: Optional[str] = None) -> int:
        """Create a new label"""
        label = Label(
            id=None,
            name=name,
            color=color,
            description=description,
            is_system=False
        )
        return self.db_manager.create_label(label)

    def add_label_to_task(self, task_id: int, label_id: int):
        """Add label to task"""
        self.db_manager.add_label_to_task(task_id, label_id)

    def remove_label_from_task(self, task_id: int, label_id: int):
        """Remove label from task"""
        self.db_manager.remove_label_from_task(task_id, label_id)

    def get_task_labels(self, task_id: int) -> List[Label]:
        """Get all labels for a task"""
        return self.db_manager.get_task_labels(task_id)

    # ==================== ATTACHMENT MANAGEMENT ====================

    def add_attachment(self, task_id: int, filename: str, original_filename: str,
                       file_path: str, file_size: int, content_type: str, uploaded_by: int) -> int:
        """Add attachment to task"""
        attachment = Attachment(
            id=None,
            task_id=task_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            content_type=content_type,
            uploaded_by=uploaded_by
        )
        return self.db_manager.create_attachment(attachment)

    def get_task_attachments(self, task_id: int) -> List[Attachment]:
        """Get all attachments for a task"""
        return self.db_manager.get_task_attachments(task_id)

    # ==================== ASSIGNMENT AND WORKFLOW ====================

    def assign_task(self, task_id: int, assignee_id: int, assigned_by: Optional[int] = None):
        """Assign task to user"""
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        old_assignee_id = task.assignee_id
        task.assignee_id = assignee_id

        self.db_manager.update_task(task)

        # Send assignment notification
        if assigned_by:
            self._notify_task_assigned(task_id, assignee_id, assigned_by, old_assignee_id)

    def bulk_update_status(self, task_ids: List[int], new_status_id: int, changed_by: Optional[int] = None):
        """Bulk update status for multiple tasks"""
        for task_id in task_ids:
            self.update_task_status(task_id, new_status_id, changed_by)

    def bulk_assign_tasks(self, task_ids: List[int], assignee_id: int, assigned_by: Optional[int] = None):
        """Bulk assign multiple tasks to user"""
        for task_id in task_ids:
            self.assign_task(task_id, assignee_id, assigned_by)

    def delete_attachment(self, attachment_id: int) -> bool:
        """Delete attachment and its file"""
        try:
            # Pobierz informacje o załączniku
            attachment = self.db_manager.get_attachment_by_id(attachment_id)
            if not attachment:
                print(f"⚠️ Attachment {attachment_id} not found")
                return False

            # Usuń z bazy danych (zwraca ścieżkę pliku)
            file_path = self.db_manager.delete_attachment(attachment_id)

            # Usuń fizyczny plik
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"🗑️ Physical file deleted: {file_path}")
                except Exception as e:
                    print(f"⚠️ Could not delete physical file: {e}")

            print(f"✅ Attachment deleted: {attachment.original_filename}")
            return True

        except Exception as e:
            print(f"❌ Error deleting attachment: {e}")
            return False

    def get_attachment_stats(self, task_id: int) -> Dict:
        """Get attachment statistics for a task"""
        attachments = self.get_task_attachments(task_id)

        total_size = sum(att.file_size or 0 for att in attachments)

        stats = {
            'count': len(attachments),
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024) if total_size > 0 else 0,
            'types': {}
        }

        # Count by type
        for att in attachments:
            if att.content_type:
                main_type = att.content_type.split('/')[0]
                stats['types'][main_type] = stats['types'].get(main_type, 0) + 1

        return stats

    def validate_attachment(self, file_path: str, max_size_mb: int = 50) -> tuple[bool, str]:
        """Validate attachment file"""
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"

            # Check file size
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024

            if file_size > max_size_bytes:
                return False, f"File too large. Maximum size: {max_size_mb}MB"

            # Check file extension (basic security)
            filename = os.path.basename(file_path)
            dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js']

            ext = os.path.splitext(filename)[1].lower()
            if ext in dangerous_extensions:
                return False, f"File type '{ext}' is not allowed for security reasons"

            return True, "Valid"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Get attachment by ID (delegate to database manager)"""
        return self.db_manager.get_attachment_by_id(attachment_id)

    # ==================== ANALYTICS AND REPORTING ====================

    def get_resolution_time_metrics(self, days: int = 30) -> Dict:
        """Get resolution time metrics for the last N days"""
        # This would typically involve complex queries
        # For now, return sample data structure
        return {
            "average_resolution_days": 5.2,
            "median_resolution_days": 3.0,
            "fastest_resolution_hours": 2.5,
            "slowest_resolution_days": 15.0,
            "resolution_by_priority": {
                "Critical": 1.2,
                "High": 3.5,
                "Medium": 7.2,
                "Low": 12.1
            }
        }

    def get_workload_distribution(self) -> Dict:
        """Get workload distribution across team members"""
        # Sample implementation - would involve database queries
        metrics = self.db_manager.get_dashboard_metrics()
        return {
            "total_open_issues": metrics.open_issues,
            "by_assignee": {
                # This would be computed from actual data
                "John Doe": 15,
                "Jane Smith": 12,
                "Bob Wilson": 8,
                "Unassigned": 5
            },
            "by_module": metrics.issues_by_module
        }

    def get_bug_trends(self, days: int = 90) -> Dict:
        """Get bug creation and resolution trends"""
        # Sample data structure for bug trends
        return {
            "bugs_created_last_30_days": 23,
            "bugs_resolved_last_30_days": 19,
            "open_bug_count": 67,
            "critical_bugs_aging": 3,
            "trend_direction": "increasing",  # increasing, decreasing, stable
            "weekly_creation_rate": 5.8,
            "weekly_resolution_rate": 4.9
        }

    # ==================== VALIDATION AND BUSINESS RULES ====================

    def _validate_task_data(self, task: Task):
        """Validate task data before saving"""
        if not task.title or not task.title.strip():
            raise ValueError("Task title is required")

        if len(task.title) > 255:
            raise ValueError("Task title must be 255 characters or less")

        if task.priority not in [1, 2, 3, 4, 5]:
            raise ValueError("Priority must be between 1 and 5")

        if task.severity not in [1, 2, 3, 4]:
            raise ValueError("Severity must be between 1 and 4")

        if not task.project_id:
            raise ValueError("Project ID is required")

        if not task.status_id:
            raise ValueError("Status ID is required")

    def _validate_business_rules(self, task: Task):
        """Validate business-specific rules"""
        # Critical bugs must have assignee
        if task.issue_type == "BUG" and task.priority == 1 and not task.assignee_id:
            raise ValueError("Critical bugs must be assigned to someone")

        # Security issues must have steps to reproduce
        if task.issue_type == "SECURITY" and not task.steps_to_reproduce:
            raise ValueError("Security issues must include steps to reproduce")

        # Performance issues should have module assigned
        if task.issue_type == "PERFORMANCE" and not task.module_id:
            print("⚠️ Warning: Performance issues should specify affected module")

    # ==================== NOTIFICATION SYSTEM ====================

    def _notify_task_created(self, task_id: int, task: Task):
        """Send notification when task is created"""
        if task.assignee_id:
            self._create_notification(
                user_id=task.assignee_id,
                task_id=task_id,
                type="assignment",
                title="New task assigned",
                message=f"You have been assigned a new {task.issue_type.lower()}: {task.title}",
                triggered_by_user_id=task.reporter_id
            )

    def _notify_task_assigned(self, task_id: int, assignee_id: int, assigned_by: int, old_assignee_id: Optional[int]):
        """Send notification when task is assigned"""
        task = self.get_task_by_id(task_id)
        if not task:
            return

        # Notify new assignee
        self._create_notification(
            user_id=assignee_id,
            task_id=task_id,
            type="assignment",
            title="Task assigned to you",
            message=f"Task '{task.title}' has been assigned to you",
            triggered_by_user_id=assigned_by
        )

        # Notify old assignee if different
        if old_assignee_id and old_assignee_id != assignee_id:
            self._create_notification(
                user_id=old_assignee_id,
                task_id=task_id,
                type="assignment",
                title="Task reassigned",
                message=f"Task '{task.title}' has been reassigned",
                triggered_by_user_id=assigned_by
            )

    def _notify_status_change(self, task_id: int, new_status_id: int, changed_by: int):
        """Send notification when task status changes"""
        task = self.get_task_by_id(task_id)
        if not task:
            return

        status_name = next((s.name for s in self.get_all_statuses() if s.id == new_status_id), "Unknown")

        # Notify assignee
        if task.assignee_id and task.assignee_id != changed_by:
            self._create_notification(
                user_id=task.assignee_id,
                task_id=task_id,
                type="status_change",
                title="Task status updated",
                message=f"Task '{task.title}' status changed to {status_name}",
                triggered_by_user_id=changed_by
            )

        # Notify reporter
        if task.reporter_id and task.reporter_id != changed_by and task.reporter_id != task.assignee_id:
            self._create_notification(
                user_id=task.reporter_id,
                task_id=task_id,
                type="status_change",
                title="Task status updated",
                message=f"Task '{task.title}' status changed to {status_name}",
                triggered_by_user_id=changed_by
            )

    def _notify_comment_added(self, task_id: int, comment_id: int, author_id: int):
        """Send notification when comment is added"""
        task = self.get_task_by_id(task_id)
        if not task:
            return

        users_to_notify = set()

        # Notify assignee
        if task.assignee_id and task.assignee_id != author_id:
            users_to_notify.add(task.assignee_id)

        # Notify reporter
        if task.reporter_id and task.reporter_id != author_id:
            users_to_notify.add(task.reporter_id)

        # TODO: Add watchers

        for user_id in users_to_notify:
            self._create_notification(
                user_id=user_id,
                task_id=task_id,
                type="comment",
                title="New comment added",
                message=f"New comment added to task '{task.title}'",
                triggered_by_user_id=author_id
            )

    def _create_notification(self, user_id: int, task_id: int, type: str, title: str,
                             message: str, triggered_by_user_id: Optional[int] = None):
        """Create a notification record"""
        notification = Notification(
            id=None,
            user_id=user_id,
            task_id=task_id,
            type=type,
            title=title,
            message=message,
            triggered_by_user_id=triggered_by_user_id
        )

        # This would be implemented in database manager
        # self.db_manager.create_notification(notification)
        print(f"📢 Notification: {title} for user {user_id}")

    def _track_task_changes(self, original_task: Task, updated_task: Task):
        """Track and log changes to task"""
        changes = []

        if original_task.title != updated_task.title:
            changes.append(f"Title changed from '{original_task.title}' to '{updated_task.title}'")

        if original_task.priority != updated_task.priority:
            changes.append(f"Priority changed from {original_task.priority} to {updated_task.priority}")

        if original_task.assignee_id != updated_task.assignee_id:
            old_assignee = original_task.assignee_name or "Unassigned"
            new_assignee = updated_task.assignee_name or "Unassigned"
            changes.append(f"Assignee changed from {old_assignee} to {new_assignee}")

        if changes:
            change_log = "; ".join(changes)
            print(f"📝 Task changes: {change_log}")

            # This could be stored in a change log table
            # self.db_manager.log_task_changes(task_id, change_log, changed_by)

    # ==================== QUICK FILTERS ====================

    def get_tasks_by_quick_filter(self, filter_type: str, user_id: Optional[int] = None) -> List[Task]:
        """Get tasks by predefined quick filters"""

        if filter_type == "my_issues" and user_id:
            return self.get_my_assigned_tasks(user_id, "open")

        elif filter_type == "all_bugs":
            search_filter = SearchFilter(issue_type="BUG")
            return self.db_manager.get_enhanced_tasks_by_filter(search_filter)

        elif filter_type == "critical_issues":
            return self.get_critical_bugs()

        elif filter_type == "trading_module":
            # Find trading module ID
            modules = self.db_manager.get_all_modules()
            trading_module = next((m for m in modules if m.name == "TRADING"), None)
            if trading_module:
                return self.get_tasks_by_module(trading_module.id)
            return []

        elif filter_type == "open_issues":
            # This would need to filter by open status IDs
            search_filter = SearchFilter()
            tasks = self.db_manager.get_enhanced_tasks_by_filter(search_filter)
            open_statuses = ["📋 To Do", "🚀 In Progress", "👀 Review", "🔒 Blocked",
                             "🔍 Triaged", "👀 Code Review", "🧪 Testing", "🔄 Reopened"]
            return [task for task in tasks if task.status_name in open_statuses]

        elif filter_type == "recent_activity":
            return self.get_recent_activity()

        else:
            return []

    # ==================== UTILITY METHODS ====================

    def get_task_summary(self, task_id: int) -> Optional[str]:
        """Get a brief summary of task for display"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        return f"{task.get_issue_type_display()} #{task.id}: {task.title}"

    def estimate_completion_date(self, task_id: int) -> Optional[datetime]:
        """Estimate completion date based on historical data"""
        task = self.get_task_by_id(task_id)
        if not task or not task.estimated_hours:
            return None

        # Simple estimation based on working hours (8 hours/day, 5 days/week)
        working_days = task.estimated_hours / 8
        return datetime.now() + timedelta(days=working_days * 7/5)  # Account for weekends

    def get_similar_tasks(self, task: Task, limit: int = 5) -> List[Task]:
        """Find similar tasks based on title and module"""
        if not task.title:
            return []

        # Simple similarity based on common words and same module
        words = task.title.lower().split()
        if len(words) < 2:
            return []

        search_query = " ".join(words[:3])  # Use first 3 words
        search_filter = SearchFilter(query=search_query, module_id=task.module_id)
        similar_tasks = self.db_manager.get_enhanced_tasks_by_filter(search_filter)

        # Exclude the current task if it has an ID
        if task.id:
            similar_tasks = [t for t in similar_tasks if t.id != task.id]

        return similar_tasks[:limit]