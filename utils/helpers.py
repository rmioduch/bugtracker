"""
Utility functions for TaskMaster - POPRAWIONA WERSJA
"""

import os
import re
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
    """Sanitize filename for safe storage"""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)

    # Remove leading/trailing underscores and dots
    filename = filename.strip('_. ')

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250-len(ext)] + ext

    return filename


def get_safe_filename(original_filename: str) -> str:
    """Generate safe unique filename"""
    import uuid

    # Sanitize original filename
    safe_name = sanitize_filename(original_filename)

    # Split name and extension
    name, ext = os.path.splitext(safe_name)

    # Generate unique filename with timestamp
    timestamp = int(datetime.now().timestamp())
    unique_id = str(uuid.uuid4())[:8]

    return f"{name}_{timestamp}_{unique_id}{ext}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if not size_bytes:
        return "0 B"

    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def get_file_icon_unicode(filename: str, content_type: str = None) -> str:
    """Get Unicode icon for file type"""
    if content_type:
        if "image" in content_type:
            return "🖼️"
        elif "pdf" in content_type:
            return "📄"
        elif "text" in content_type:
            return "📝"
        elif "video" in content_type:
            return "🎥"
        elif "audio" in content_type:
            return "🎵"
        elif "zip" in content_type or "archive" in content_type:
            return "📦"
        elif "excel" in content_type or "spreadsheet" in content_type:
            return "📊"
        elif "word" in content_type or "document" in content_type:
            return "📄"

    # Fallback based on extension
    ext = os.path.splitext(filename)[1].lower()

    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg']
    document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
    spreadsheet_extensions = ['.xlsx', '.xls', '.csv', '.ods']
    archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz']
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    code_extensions = ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']

    if ext in image_extensions:
        return "🖼️"
    elif ext in document_extensions:
        return "📄"
    elif ext in spreadsheet_extensions:
        return "📊"
    elif ext in archive_extensions:
        return "📦"
    elif ext in video_extensions:
        return "🎥"
    elif ext in audio_extensions:
        return "🎵"
    elif ext in code_extensions:
        return "💻"
    elif ext == '.log':
        return "📋"
    else:
        return "📎"


def validate_file_security(filename: str) -> tuple[bool, str]:
    """Validate file for security risks"""
    # Dangerous extensions
    dangerous_extensions = [
        '.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jar',
        '.com', '.pif', '.msi', '.reg', '.hta', '.cpl'
    ]

    ext = os.path.splitext(filename)[1].lower()

    if ext in dangerous_extensions:
        return False, f"File type '{ext}' is blocked for security reasons"

    # Check for double extensions (e.g., file.txt.exe)
    if filename.count('.') > 1:
        parts = filename.split('.')
        if len(parts) > 2 and parts[-1].lower() in [e[1:] for e in dangerous_extensions]:
            return False, "Suspicious double extension detected"

    # Check filename length
    if len(filename) > 255:
        return False, "Filename too long (max 255 characters)"

    # Check for suspicious patterns
    suspicious_patterns = [
        r'\.\./',  # Path traversal
        r'[<>:"|?*]',  # Invalid filename characters
        r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)',  # Windows reserved names
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            return False, "Suspicious filename pattern detected"

    return True, "File is safe"


def create_attachment_thumbnail(file_path: str, thumbnail_dir: str, size: tuple = (200, 200)) -> Optional[str]:
    """Create thumbnail for image attachments (requires PIL)"""
    try:
        from PIL import Image

        # Check if it's an image
        try:
            with Image.open(file_path) as img:
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # Generate thumbnail filename
                filename = os.path.basename(file_path)
                name, _ = os.path.splitext(filename)
                thumbnail_filename = f"thumb_{name}.png"
                thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

                # Ensure thumbnail directory exists
                os.makedirs(thumbnail_dir, exist_ok=True)

                # Save thumbnail
                img.save(thumbnail_path, 'PNG')
                return thumbnail_path

        except Exception:
            # Not an image or cannot process
            return None

    except ImportError:
        # PIL not installed
        return None


def cleanup_orphaned_attachments(attachments_dir: str, database_manager) -> int:
    """Clean up attachment files that no longer exist in database"""
    if not os.path.exists(attachments_dir):
        return 0

    try:
        # Get all attachment file paths from database
        conn = database_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM attachments")
        db_files = {row[0] for row in cursor.fetchall()}

        # Get all files in attachments directory
        deleted_count = 0
        for filename in os.listdir(attachments_dir):
            file_path = os.path.join(attachments_dir, filename)
            if os.path.isfile(file_path) and file_path not in db_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"🗑️ Cleaned up orphaned file: {filename}")
                except Exception as e:
                    print(f"⚠️ Could not delete orphaned file {filename}: {e}")

        return deleted_count

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return 0


def get_attachment_directory() -> str:
    """Get the attachments directory path"""
    app_data_dir = get_app_data_dir()
    attachments_dir = os.path.join(app_data_dir, 'attachments')
    os.makedirs(attachments_dir, exist_ok=True)
    return attachments_dir


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


def create_default_user_if_needed(database_manager):
    """Create default admin user if no users exist - NOWA FUNKCJA"""
    try:
        users = database_manager.get_all_users()
        if not users:
            print("🔧 Creating default admin user...")

            from models.entities import User

            default_user = User(
                id=None,
                username="admin",
                email="admin@taskmaster.local",
                full_name="System Administrator",
                role="ADMIN",
                avatar_url=None,
                is_active=True
            )

            user_id = database_manager.create_user(default_user)
            print(f"✅ Default user created with ID: {user_id}")
            print("📝 Login: admin, Email: admin@taskmaster.local")

            return user_id
        else:
            print(f"👥 Found {len(users)} existing users")
            return users[0].id  # Return first user ID

    except Exception as e:
        print(f"❌ Error creating default user: {e}")
        return 1  # Fallback to ID 1


def setup_application_directories():
    """Setup all required application directories - NOWA FUNKCJA"""
    try:
        app_dir = get_app_data_dir()
        attachments_dir = get_attachment_directory()

        # Create additional directories if needed
        logs_dir = os.path.join(app_dir, 'logs')
        backups_dir = os.path.join(app_dir, 'backups')
        temp_dir = os.path.join(app_dir, 'temp')

        for directory in [logs_dir, backups_dir, temp_dir]:
            os.makedirs(directory, exist_ok=True)

        print(f"📁 Application directories ready:")
        print(f"   App data: {app_dir}")
        print(f"   Attachments: {attachments_dir}")
        print(f"   Logs: {logs_dir}")
        print(f"   Backups: {backups_dir}")
        print(f"   Temp: {temp_dir}")

        return {
            'app_dir': app_dir,
            'attachments_dir': attachments_dir,
            'logs_dir': logs_dir,
            'backups_dir': backups_dir,
            'temp_dir': temp_dir
        }

    except Exception as e:
        print(f"❌ Error setting up directories: {e}")
        raise


def initialize_application():
    """Initialize the application with all required setup - NOWA FUNKCJA"""
    try:
        print("🚀 Initializing TaskMaster application...")

        # 1. Setup directories
        dirs = setup_application_directories()

        # 2. Initialize database
        from models.database import DatabaseManager
        db_manager = DatabaseManager()
        db_manager.initialize_database()

        # 3. Create default user if needed
        user_id = create_default_user_if_needed(db_manager)

        print("✅ Application initialized successfully!")
        return {
            'db_manager': db_manager,
            'default_user_id': user_id,
            'directories': dirs
        }

    except Exception as e:
        print(f"❌ Application initialization failed: {e}")
        raise


def validate_attachment_upload(file_path: str, existing_attachments: list, config: dict) -> tuple[bool, str]:
    """Validate attachment upload against limits and security - NOWA FUNKCJA"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Get file info
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)

        # Check individual file size
        max_file_size = config.get('max_file_size_mb', 50) * 1024 * 1024
        if file_size > max_file_size:
            return False, f"File too large. Maximum size: {config.get('max_file_size_mb', 50)}MB"

        # Check total attachments count
        current_count = len(existing_attachments)
        max_files = config.get('max_files_per_task', 20)
        if current_count >= max_files:
            return False, f"Too many attachments. Maximum: {max_files} files per task"

        # Check total size
        current_total_size = sum(att.file_size or 0 for att in existing_attachments)
        max_total_size = config.get('max_total_size_mb', 200) * 1024 * 1024
        if current_total_size + file_size > max_total_size:
            return False, f"Total size would exceed limit of {config.get('max_total_size_mb', 200)}MB"

        # Security validation
        is_safe, security_msg = validate_file_security(filename)
        if not is_safe:
            return False, security_msg

        # Check allowed extensions
        ext = os.path.splitext(filename)[1].lower()
        allowed_extensions = config.get('allowed_extensions', [])
        blocked_extensions = config.get('blocked_extensions', [])

        if blocked_extensions and ext in blocked_extensions:
            return False, f"File type '{ext}' is blocked"

        if allowed_extensions and ext not in allowed_extensions:
            return False, f"File type '{ext}' is not allowed"

        return True, "File is valid for upload"

    except Exception as e:
        return False, f"Validation error: {str(e)}"


def get_file_type_category(filename: str, content_type: str = None) -> str:
    """Get file type category for organization - NOWA FUNKCJA"""
    if content_type:
        if content_type.startswith('image/'):
            return "Image"
        elif content_type.startswith('video/'):
            return "Video"
        elif content_type.startswith('audio/'):
            return "Audio"
        elif 'pdf' in content_type:
            return "Document"
        elif any(doc_type in content_type for doc_type in ['document', 'word', 'spreadsheet', 'excel']):
            return "Document"
        elif any(archive_type in content_type for archive_type in ['zip', 'archive', 'compressed']):
            return "Archive"
        elif content_type.startswith('text/'):
            return "Text"

    # Fallback to extension-based detection
    ext = os.path.splitext(filename)[1].lower()

    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg']:
        return "Image"
    elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
        return "Video"
    elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
        return "Audio"
    elif ext in ['.pdf', '.doc', '.docx', '.odt', '.rtf']:
        return "Document"
    elif ext in ['.xlsx', '.xls', '.csv', '.ods']:
        return "Spreadsheet"
    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return "Archive"
    elif ext in ['.txt', '.log', '.md', '.json', '.xml', '.yaml']:
        return "Text"
    elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php']:
        return "Code"
    else:
        return "Other"


def format_attachment_info(attachment) -> str:
    """Format attachment information for display - NOWA FUNKCJA"""
    info_parts = []

    # File type category
    category = get_file_type_category(attachment.original_filename, attachment.content_type)
    info_parts.append(f"Type: {category}")

    # File size
    size_str = format_file_size(attachment.file_size)
    info_parts.append(f"Size: {size_str}")

    # Upload date
    if attachment.uploaded_at:
        date_str = attachment.uploaded_at.strftime("%Y-%m-%d %H:%M")
        info_parts.append(f"Uploaded: {date_str}")

    # Uploader
    if attachment.uploaded_by_name:
        info_parts.append(f"By: {attachment.uploaded_by_name}")

    return " • ".join(info_parts)