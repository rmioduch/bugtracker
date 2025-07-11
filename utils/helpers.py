"""
Utility functions for TaskMaster
"""

from datetime import datetime
from typing import Optional


def format_date(date: datetime, include_time: bool = False) -> str:
    """Format datetime for display"""
    if not date:
        return ""

    if include_time:
        return date.strftime("%Y-%m-%d %H:%M")
    else:
        return date.strftime("%Y-%m-%d")


def format_relative_date(date: datetime) -> str:
    """Format date relative to now (e.g., '2 days ago')"""
    if not date:
        return ""

    now = datetime.now()
    diff = now - date

    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            if minutes == 0:
                return "Just now"
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif diff.days < 365:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length"""
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


def validate_non_empty(value: str, field_name: str) -> bool:
    """Validate that a string field is not empty"""
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    return filename


def get_priority_color(priority: int) -> str:
    """Get color for priority level"""
    colors = {
        1: "#EF4444",  # High - Red
        2: "#F59E0B",  # Medium - Yellow
        3: "#10B981"   # Low - Green
    }
    return colors.get(priority, "#6B7280")


def get_priority_name(priority: int) -> str:
    """Get name for priority level"""
    names = {
        1: "High",
        2: "Medium",
        3: "Low"
    }
    return names.get(priority, "Unknown")


def get_status_color(status_name: str) -> str:
    """Get color for status"""
    color_map = {
        "📋 To Do": "#6B7280",
        "🚀 In Progress": "#3B82F6",
        "👀 Review": "#F59E0B",
        "🔒 Blocked": "#EF4444",
        "✅ Done": "#10B981"
    }
    return color_map.get(status_name, "#6B7280")


def calculate_completion_percentage(stats: dict) -> float:
    """Calculate completion percentage from statistics"""
    total_tasks = sum(stats.values())
    if total_tasks == 0:
        return 0.0

    completed_tasks = stats.get("✅ Done", 0)
    return (completed_tasks / total_tasks) * 100


def export_tasks_to_csv(tasks: list, filename: str):
    """Export tasks list to CSV file"""
    import csv

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', 'Title', 'Project', 'Status', 'Priority', 'Created', 'Updated', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for task in tasks:
            writer.writerow({
                'ID': task.id,
                'Title': task.title,
                'Project': task.project_name or '',
                'Status': task.status_name or '',
                'Priority': get_priority_name(task.priority),
                'Created': format_date(task.created_at, True) if task.created_at else '',
                'Updated': format_date(task.updated_at, True) if task.updated_at else '',
                'Description': task.description or ''
            })


def backup_database(db_path: str, backup_path: str):
    """Create backup of database"""
    import shutil
    import os

    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        return True
    return False


def get_app_data_dir() -> str:
    """Get application data directory"""
    import os
    from pathlib import Path

    if os.name == 'nt':  # Windows
        base_dir = os.environ.get('APPDATA', str(Path.home()))
    else:  # macOS, Linux
        base_dir = str(Path.home() / '.local' / 'share')

    app_dir = os.path.join(base_dir, 'TaskMaster')
    os.makedirs(app_dir, exist_ok=True)

    return app_dir