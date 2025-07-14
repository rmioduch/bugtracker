"""
Enhanced data classes for TaskMaster BugTracker - Money Mentor AI
"""
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ENUMS dla lepszej organizacji
class IssueType(Enum):
    BUG = "BUG"
    FEATURE = "FEATURE"
    ENHANCEMENT = "ENHANCEMENT"
    TASK = "TASK"
    DOCUMENTATION = "DOCUMENTATION"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    REFACTOR = "REFACTOR"


class Priority(Enum):
    CRITICAL = 1  # P0
    HIGH = 2      # P1
    MEDIUM = 3    # P2
    LOW = 4       # P3
    TRIVIAL = 5   # P4


class Severity(Enum):
    BLOCKER = 1
    MAJOR = 2
    MINOR = 3
    TRIVIAL = 4


class UserRole(Enum):
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"
    TESTER = "TESTER"
    REPORTER = "REPORTER"
    VIEWER = "VIEWER"


class IssueStatus(Enum):
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    CODE_REVIEW = "CODE_REVIEW"
    TESTING = "TESTING"
    VERIFICATION = "VERIFICATION"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"
    DUPLICATE = "DUPLICATE"
    WONT_FIX = "WONT_FIX"
    CANNOT_REPRODUCE = "CANNOT_REPRODUCE"


class ResolutionType(Enum):
    FIXED = "FIXED"
    WONT_FIX = "WONT_FIX"
    DUPLICATE = "DUPLICATE"
    INVALID = "INVALID"
    WORKS_AS_DESIGNED = "WORKS_AS_DESIGNED"
    CANNOT_REPRODUCE = "CANNOT_REPRODUCE"


class MoneyMentorModule(Enum):
    CORE = "CORE"
    TRADING = "TRADING"
    BROKER = "BROKER"
    STRATEGY = "STRATEGY"
    RISK = "RISK"
    PORTFOLIO = "PORTFOLIO"
    ANALYSIS = "ANALYSIS"
    DATA = "DATA"
    UI = "UI"
    DB = "DB"
    API = "API"
    REPORTING = "REPORTING"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    TESTING = "TESTING"


# EXISTING MODELS (zachowujemy istniejące)
@dataclass
class Project:
    """Project entity - bez zmian"""
    id: Optional[int]
    name: str
    description: Optional[str]
    created_at: Optional[datetime] = None


@dataclass
class TaskStatus:
    """Task status entity - rozszerzone o nowe statusy"""
    id: int
    name: str
    color: str
    sort_order: int


@dataclass
class Comment:
    """Comment entity - bez zmian"""
    id: Optional[int]
    task_id: int
    content: str
    created_at: Optional[datetime] = None
    # DODANE:
    author_id: Optional[int] = None
    author_name: Optional[str] = None


@dataclass
class StatusHistory:
    """Status change history entity - bez zmian"""
    id: Optional[int]
    task_id: int
    old_status_id: Optional[int]
    new_status_id: int
    changed_at: Optional[datetime] = None
    # DODANE:
    changed_by: Optional[int] = None


# NEW MODELS dla bugtrackera

@dataclass
class User:
    """User entity for bug tracker"""
    id: Optional[int]
    username: str
    email: str
    full_name: str
    role: str  # UserRole enum value
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    def get_display_name(self) -> str:
        """Return display name (full_name or username)"""
        return self.full_name if self.full_name else self.username


@dataclass
class Module:
    """Money Mentor AI module/component"""
    id: Optional[int]
    name: str  # MoneyMentorModule enum value
    display_name: str
    description: Optional[str]
    component_lead_id: Optional[int] = None
    component_lead_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


@dataclass
class Version:
    """Version/Release entity"""
    id: Optional[int]
    name: str  # e.g. "v2.1.0", "Sprint 15"
    description: Optional[str]
    release_date: Optional[datetime] = None
    status: str = "PLANNED"  # PLANNED, IN_PROGRESS, RELEASED
    created_at: Optional[datetime] = None


@dataclass
class Label:
    """Label/Tag entity"""
    id: Optional[int]
    name: str
    color: str  # Hex color code
    description: Optional[str]
    is_system: bool = False  # System labels vs user-created
    created_at: Optional[datetime] = None


@dataclass
class Attachment:
    """File attachment entity"""
    id: Optional[int]
    task_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int  # in bytes
    content_type: str  # MIME type
    uploaded_by: int
    uploaded_by_name: Optional[str] = None
    uploaded_at: Optional[datetime] = None

    def get_file_size_mb(self) -> str:
        """Get file size in MB format"""
        if self.file_size:
            mb = self.file_size / (1024 * 1024)
            return f"{mb:.2f}"
        return "0.00"

    def get_file_size_human(self) -> str:
        """Get file size in human readable format"""
        if not self.file_size:
            return "0 B"

        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                if unit == 'B':
                    return f"{int(size)} {unit}"
                else:
                    return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def is_image(self) -> bool:
        """Check if attachment is an image"""
        if self.content_type:
            return self.content_type.startswith('image/')

        # Fallback to extension
        ext = os.path.splitext(self.original_filename)[1].lower()
        return ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff']

    def is_document(self) -> bool:
        """Check if attachment is a document"""
        if self.content_type:
            return (self.content_type.startswith('text/') or
                    'pdf' in self.content_type or
                    'document' in self.content_type or
                    'word' in self.content_type)

        ext = os.path.splitext(self.original_filename)[1].lower()
        return ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']

    def is_video(self) -> bool:
        """Check if attachment is a video"""
        if self.content_type:
            return self.content_type.startswith('video/')

        ext = os.path.splitext(self.original_filename)[1].lower()
        return ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']

    def is_archive(self) -> bool:
        """Check if attachment is an archive"""
        if self.content_type:
            return ('zip' in self.content_type or
                    'archive' in self.content_type or
                    'compressed' in self.content_type)

        ext = os.path.splitext(self.original_filename)[1].lower()
        return ext in ['.zip', '.rar', '.7z', '.tar', '.gz']

    def get_file_extension(self) -> str:
        """Get file extension"""
        return os.path.splitext(self.original_filename)[1].lower()

    def get_display_name(self, max_length: int = 30) -> str:
        """Get display name truncated if too long"""
        if len(self.original_filename) <= max_length:
            return self.original_filename

        name, ext = os.path.splitext(self.original_filename)
        truncated_name = name[:max_length - len(ext) - 3] + "..."
        return truncated_name + ext


@dataclass
class TaskDependency:
    """Task dependency relationship"""
    id: Optional[int]
    task_id: int
    depends_on_task_id: int
    dependency_type: str = "blocks"  # blocks, related_to, duplicates
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None


@dataclass
class Watcher:
    """Task watcher entity"""
    id: Optional[int]
    task_id: int
    user_id: int
    user_name: Optional[str] = None
    added_at: Optional[datetime] = None


@dataclass
class Notification:
    """Notification entity"""
    id: Optional[int]
    user_id: int
    task_id: int
    type: str  # 'assignment', 'status_change', 'comment', 'mention'
    title: str
    message: str
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    # Extra data for rich notifications
    action_url: Optional[str] = None
    triggered_by_user_id: Optional[int] = None
    triggered_by_user_name: Optional[str] = None


# ENHANCED TASK MODEL
@dataclass
class Task:
    """Enhanced Task entity for bug tracking"""
    # Original fields
    id: Optional[int]
    project_id: int
    title: str
    description: Optional[str]
    status_id: int
    priority: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None
    status_name: Optional[str] = None

    # NEW BUG TRACKER FIELDS

    # Issue classification
    issue_type: str = IssueType.TASK.value
    severity: int = Severity.MINOR.value

    # People
    reporter_id: Optional[int] = None
    reporter_name: Optional[str] = None
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None

    # Module/Component
    module_id: Optional[int] = None
    module_name: Optional[str] = None

    # Versions
    affected_version_id: Optional[int] = None
    affected_version_name: Optional[str] = None
    fix_version_id: Optional[int] = None
    fix_version_name: Optional[str] = None

    # Bug reproduction info
    environment: Optional[str] = None  # "Windows 11, Java 23, Exante Broker"
    steps_to_reproduce: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    stack_trace: Optional[str] = None

    # Resolution
    resolution: Optional[str] = None  # ResolutionType enum value
    resolution_notes: Optional[str] = None
    duplicate_of: Optional[int] = None

    # Time tracking
    estimated_hours: Optional[float] = None
    time_spent: Optional[float] = None

    # Labels (will be loaded separately)
    labels: List[Label] = None

    # Counts for UI
    comments_count: int = 0
    attachments_count: int = 0
    watchers_count: int = 0
    dependencies_count: int = 0

    def __post_init__(self):
        """Initialize labels list if None"""
        if self.labels is None:
            self.labels = []

    def get_issue_type_display(self) -> str:
        """Get display name for issue type"""
        type_map = {
            'BUG': '🐛 Bug',
            'FEATURE': '✨ Feature Request',
            'ENHANCEMENT': '🔧 Enhancement',
            'TASK': '📋 Task',
            'DOCUMENTATION': '📚 Documentation',
            'PERFORMANCE': '⚡ Performance',
            'SECURITY': '🔒 Security',
            'REFACTOR': '♻️ Refactoring'
        }
        return type_map.get(self.issue_type, self.issue_type)

    def get_priority_display(self) -> str:
        """Get display name for priority"""
        priority_map = {
            1: '🔴 Critical (P0)',
            2: '🟠 High (P1)',
            3: '🟡 Medium (P2)',
            4: '🟢 Low (P3)',
            5: '⚪ Trivial (P4)'
        }
        return priority_map.get(self.priority, f'Priority {self.priority}')

    def get_severity_display(self) -> str:
        """Get display name for severity"""
        severity_map = {
            1: '🛑 Blocker',
            2: '🔴 Major',
            3: '🟡 Minor',
            4: '🟢 Trivial'
        }
        return severity_map.get(self.severity, f'Severity {self.severity}')

    def is_bug(self) -> bool:
        """Check if this is a bug issue"""
        return self.issue_type == IssueType.BUG.value

    def is_critical(self) -> bool:
        """Check if this is critical priority"""
        return self.priority == Priority.CRITICAL.value

    def is_blocker(self) -> bool:
        """Check if this is blocker severity"""
        return self.severity == Severity.BLOCKER.value

    def get_age_days(self) -> int:
        """Get age in days since creation"""
        if not self.created_at:
            return 0
        return (datetime.now() - self.created_at).days

    def has_labels(self) -> bool:
        """Check if task has any labels"""
        return self.labels and len(self.labels) > 0


# SEARCH AND FILTER MODELS

@dataclass
class SearchFilter:
    """Search filter criteria"""
    query: Optional[str] = None
    project_id: Optional[int] = None
    issue_type: Optional[str] = None
    status_id: Optional[int] = None
    priority: Optional[int] = None
    severity: Optional[int] = None
    assignee_id: Optional[int] = None
    reporter_id: Optional[int] = None
    module_id: Optional[int] = None
    labels: List[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    updated_from: Optional[datetime] = None
    updated_to: Optional[datetime] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = []


@dataclass
class DashboardMetrics:
    """Dashboard metrics data"""
    total_issues: int = 0
    open_issues: int = 0
    closed_issues: int = 0
    critical_bugs: int = 0
    my_assigned: int = 0
    recently_updated: int = 0

    # By module breakdown
    issues_by_module: dict = None

    # By status breakdown
    issues_by_status: dict = None

    # Trends
    issues_created_this_week: int = 0
    issues_resolved_this_week: int = 0
    average_resolution_days: float = 0.0

    def __post_init__(self):
        if self.issues_by_module is None:
            self.issues_by_module = {}
        if self.issues_by_status is None:
            self.issues_by_status = {}


# CONSTANTS for UI

ISSUE_TYPE_CHOICES = [
    ('BUG', '🐛 Bug'),
    ('FEATURE', '✨ Feature Request'),
    ('ENHANCEMENT', '🔧 Enhancement'),
    ('TASK', '📋 Task'),
    ('DOCUMENTATION', '📚 Documentation'),
    ('PERFORMANCE', '⚡ Performance'),
    ('SECURITY', '🔒 Security'),
    ('REFACTOR', '♻️ Refactoring')
]

PRIORITY_CHOICES = [
    (1, '🔴 Critical (P0)'),
    (2, '🟠 High (P1)'),
    (3, '🟡 Medium (P2)'),
    (4, '🟢 Low (P3)'),
    (5, '⚪ Trivial (P4)')
]

SEVERITY_CHOICES = [
    (1, '🛑 Blocker'),
    (2, '🔴 Major'),
    (3, '🟡 Minor'),
    (4, '🟢 Trivial')
]

RESOLUTION_CHOICES = [
    ('FIXED', '✅ Fixed'),
    ('WONT_FIX', '❌ Won\'t Fix'),
    ('DUPLICATE', '👥 Duplicate'),
    ('INVALID', '❓ Invalid'),
    ('WORKS_AS_DESIGNED', '🎯 Works as Designed'),
    ('CANNOT_REPRODUCE', '🔍 Cannot Reproduce')
]

MODULE_CHOICES = [
    ('CORE', '🏗️ Core System'),
    ('TRADING', '📈 Trading Module'),
    ('BROKER', '🔗 Broker Integration'),
    ('STRATEGY', '🧠 Strategy Engine'),
    ('RISK', '⚠️ Risk Management'),
    ('PORTFOLIO', '💼 Portfolio Management'),
    ('ANALYSIS', '📊 Technical Analysis'),
    ('DATA', '💾 Data Management'),
    ('UI', '🎨 User Interface'),
    ('DB', '🗄️ Database'),
    ('API', '🔌 API Integrations'),
    ('REPORTING', '📋 Reports & Visualization'),
    ('SECURITY', '🔒 Security'),
    ('PERFORMANCE', '⚡ Performance'),
    ('TESTING', '🧪 Testing Framework')
]

# Default system labels
DEFAULT_LABELS = [
    ('performance-critical', '#FF4444', 'Performance critical issue'),
    ('customer-reported', '#4444FF', 'Reported by customer'),
    ('regression', '#FF8800', 'Regression bug'),
    ('hotfix-candidate', '#FF0000', 'Candidate for hotfix'),
    ('breaking-change', '#8800FF', 'Breaking change'),
    ('api-change', '#00FF88', 'API change required'),
    ('database-migration', '#0088FF', 'Requires database migration'),
    ('easy-fix', '#88FF00', 'Easy fix for new developers'),
    ('needs-investigation', '#FFAA00', 'Needs further investigation'),
    ('external-dependency', '#AA00FF', 'Depends on external system')
]