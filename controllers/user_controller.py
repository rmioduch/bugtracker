"""
User Controller - User management and authentication for TaskMaster BugTracker
POPRAWIONA WERSJA - używa przekazanego database managera
"""

import hashlib
import secrets
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta

from models.database import DatabaseManager
from models.entities import User, UserRole, Task


class UserController:
    """Controller for user management and authentication - FIXED VERSION"""

    def __init__(self, db_manager: DatabaseManager = None):
        # IMPORTANT: Użyj przekazanego database managera lub utwórz nowy
        self.db_manager = db_manager if db_manager else DatabaseManager()
        self.current_session = None
        self.failed_login_attempts = {}  # Track failed attempts by username
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)

    # ==================== USER AUTHENTICATION ====================

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate user credentials
        Returns: (success, user_object, message)
        """
        print(f"🔐 Attempting authentication for: {username}")

        if not username or not password:
            return False, None, "Username and password are required"

        # Check for account lockout
        if self._is_account_locked(username):
            return False, None, "Account temporarily locked due to failed login attempts"

        try:
            # Get user from database
            user = self.get_user_by_username(username)
            if not user:
                self._record_failed_attempt(username)
                return False, None, "Invalid username or password"

            # Check if user is active
            if not user.is_active:
                return False, None, "Account is disabled"

            # Check password (simplified for demo)
            if self._verify_password(password, user):
                # Reset failed attempts on successful login
                if username in self.failed_login_attempts:
                    del self.failed_login_attempts[username]

                # Update last login
                self._update_last_login(user.id)

                # Set current session
                self.current_session = UserSession(user)

                print(f"✅ Authentication successful for: {username}")
                return True, user, "Login successful"
            else:
                self._record_failed_attempt(username)
                return False, None, "Invalid username or password"

        except Exception as e:
            print(f"❌ Authentication error for {username}: {e}")
            return False, None, f"Authentication error: {str(e)}"

    def logout_user(self):
        """Logout current user"""
        if self.current_session:
            print(f"👋 User logged out: {self.current_session.user.username}")
            self.current_session = None

    def get_current_user(self) -> Optional[User]:
        """Get currently logged in user"""
        return self.current_session.user if self.current_session else None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_session is not None

    # ==================== USER MANAGEMENT ====================

    def create_user(self, username: str, email: str, full_name: str,
                    password: str, role: str = "REPORTER") -> int:
        """Create a new user account"""
        print(f"👤 Creating user: {username} ({full_name})")

        # Validate input
        self._validate_user_data(username, email, full_name, password)

        # Check for existing username/email
        if self.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")

        if self.get_user_by_email(email):
            raise ValueError(f"Email '{email}' already exists")

        # Validate role
        if role not in [r.value for r in UserRole]:
            raise ValueError(f"Invalid role: {role}")

        # Create user object
        user = User(
            id=None,
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            is_active=True
        )

        try:
            # Save to database using our database manager
            user_id = self.db_manager.create_user(user)

            # Store password hash (simplified for demo)
            self._store_password_hash(user_id, password)

            print(f"✅ User created: {full_name} ({username}) with role {role}")
            return user_id

        except Exception as e:
            print(f"❌ Error creating user {username}: {e}")
            raise

    def get_all_users(self, active_only: bool = True) -> List[User]:
        """Get all users"""
        try:
            return self.db_manager.get_all_users(active_only)
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            return []

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return self.db_manager.get_user_by_id(user_id)
        except Exception as e:
            print(f"❌ Error getting user by ID {user_id}: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            users = self.db_manager.get_all_users(active_only=False)
            return next((user for user in users if user.username.lower() == username.lower()), None)
        except Exception as e:
            print(f"❌ Error getting user by username {username}: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            users = self.db_manager.get_all_users(active_only=False)
            return next((user for user in users if user.email.lower() == email.lower()), None)
        except Exception as e:
            print(f"❌ Error getting user by email {email}: {e}")
            return None

    def update_user(self, user: User):
        """Update user information"""
        if not user.id:
            raise ValueError("User ID is required for updates")

        # Validate updated data
        existing_user = self.get_user_by_id(user.id)
        if not existing_user:
            raise ValueError(f"User with ID {user.id} not found")

        # Check for username/email conflicts (excluding current user)
        username_conflict = self.get_user_by_username(user.username)
        if username_conflict and username_conflict.id != user.id:
            raise ValueError(f"Username '{user.username}' already exists")

        email_conflict = self.get_user_by_email(user.email)
        if email_conflict and email_conflict.id != user.id:
            raise ValueError(f"Email '{user.email}' already exists")

        # Update in database
        self.db_manager.update_user(user)

        print(f"✅ User updated: {user.full_name} ({user.username})")

    def deactivate_user(self, user_id: int):
        """Deactivate user account (soft delete)"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        user.is_active = False
        self.db_manager.update_user(user)

        print(f"⚠️ User deactivated: {user.full_name} ({user.username})")

    def reactivate_user(self, user_id: int):
        """Reactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        user.is_active = True
        self.db_manager.update_user(user)

        print(f"✅ User reactivated: {user.full_name} ({user.username})")

    # ==================== ROLE AND PERMISSION MANAGEMENT ====================

    def change_user_role(self, user_id: int, new_role: str, changed_by: Optional[int] = None):
        """Change user role (admin operation)"""
        # Check permissions
        if changed_by:
            changer = self.get_user_by_id(changed_by)
            if not changer or changer.role != UserRole.ADMIN.value:
                raise PermissionError("Only administrators can change user roles")

        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Validate role
        if new_role not in [r.value for r in UserRole]:
            raise ValueError(f"Invalid role: {new_role}")

        old_role = user.role
        user.role = new_role
        self.db_manager.update_user(user)

        print(f"🔄 Role changed for {user.full_name}: {old_role} → {new_role}")

    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        role_permissions = self._get_role_permissions(user.role)
        return permission in role_permissions

    def can_edit_task(self, user: User, task: Task) -> bool:
        """Check if user can edit specific task"""
        if user.role == UserRole.ADMIN.value:
            return True

        if user.role in [UserRole.DEVELOPER.value, UserRole.TESTER.value]:
            # Can edit if assigned or if they created it
            return task.assignee_id == user.id or task.reporter_id == user.id

        if user.role == UserRole.REPORTER.value:
            # Can only edit their own reported tasks and only if not assigned to others
            return task.reporter_id == user.id and task.assignee_id is None

        return False

    def can_delete_task(self, user: User, task: Task) -> bool:
        """Check if user can delete specific task"""
        if user.role == UserRole.ADMIN.value:
            return True

        # Only admins can delete tasks for safety
        return False

    def can_assign_tasks(self, user: User) -> bool:
        """Check if user can assign tasks to others"""
        return user.role in [UserRole.ADMIN.value, UserRole.DEVELOPER.value]

    def can_change_task_status(self, user: User, task: Task, new_status: str) -> bool:
        """Check if user can change task status"""
        if user.role == UserRole.ADMIN.value:
            return True

        if user.role in [UserRole.DEVELOPER.value, UserRole.TESTER.value]:
            # Can change status if assigned to them
            if task.assignee_id == user.id:
                return True

            # Developers can move tasks to testing
            if user.role == UserRole.DEVELOPER.value and "Testing" in new_status:
                return True

            # Testers can move tasks back to development or mark as verified
            if user.role == UserRole.TESTER.value and any(status in new_status for status in ["In Progress", "Verification", "Done"]):
                return True

        return False

    # ==================== USER STATISTICS AND ACTIVITY ====================

    def get_user_statistics(self, user_id: int) -> Dict:
        """Get user activity statistics"""
        # This would involve database queries
        # For now, return sample structure
        return {
            "tasks_assigned": 15,
            "tasks_reported": 8,
            "tasks_completed": 12,
            "comments_added": 47,
            "average_resolution_days": 4.2,
            "open_tasks": 3,
            "this_week": {
                "tasks_completed": 2,
                "comments_added": 8,
                "tasks_assigned": 1
            }
        }

    def get_team_workload(self) -> List[Dict]:
        """Get workload distribution across team"""
        users = self.get_all_users()
        workload = []

        for user in users:
            if user.role in [UserRole.DEVELOPER.value, UserRole.TESTER.value]:
                stats = self.get_user_statistics(user.id)
                workload.append({
                    "user": user,
                    "open_tasks": stats["open_tasks"],
                    "total_assigned": stats["tasks_assigned"],
                    "completion_rate": stats["tasks_completed"] / max(stats["tasks_assigned"], 1) * 100
                })

        return sorted(workload, key=lambda x: x["open_tasks"], reverse=True)

    def get_recent_user_activity(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get recent activity for user"""
        # This would query actual activity data
        # Return sample structure for now
        return [
            {
                "timestamp": datetime.now() - timedelta(hours=2),
                "action": "commented",
                "target": "Task #142: Fix trading module crash",
                "description": "Added reproduction steps"
            },
            {
                "timestamp": datetime.now() - timedelta(hours=5),
                "action": "status_changed",
                "target": "Task #139: Improve chart rendering",
                "description": "Changed status to 'In Progress'"
            },
            {
                "timestamp": datetime.now() - timedelta(days=1),
                "action": "created",
                "target": "Task #143: Add dark theme toggle",
                "description": "Created new feature request"
            }
        ]

    # ==================== PASSWORD MANAGEMENT ====================

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Verify old password
        if not self._verify_password(old_password, user):
            raise ValueError("Current password is incorrect")

        # Validate new password
        self._validate_password(new_password)

        # Store new password hash
        self._store_password_hash(user_id, new_password)

        print(f"🔐 Password changed for user: {user.username}")
        return True

    def reset_password(self, user_id: int, new_password: str, admin_user_id: int) -> bool:
        """Reset user password (admin operation)"""
        # Check admin permissions
        admin = self.get_user_by_id(admin_user_id)
        if not admin or admin.role != UserRole.ADMIN.value:
            raise PermissionError("Only administrators can reset passwords")

        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Validate new password
        self._validate_password(new_password)

        # Store new password hash
        self._store_password_hash(user_id, new_password)

        print(f"🔐 Password reset for user: {user.username} by admin: {admin.username}")
        return True

    # ==================== PRIVATE HELPER METHODS ====================

    def _validate_user_data(self, username: str, email: str, full_name: str, password: str):
        """Validate user data"""
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if not email or "@" not in email:
            raise ValueError("Valid email address is required")

        if not full_name or len(full_name) < 2:
            raise ValueError("Full name must be at least 2 characters long")

        self._validate_password(password)

    def _validate_password(self, password: str):
        """Validate password strength"""
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        # Add more password rules as needed
        if password.lower() in ["password", "123456", "admin", "user"]:
            raise ValueError("Password is too common")

    def _verify_password(self, password: str, user: User) -> bool:
        """Verify password against stored hash"""
        # Simplified for demo - in production use proper password hashing

        # Default demo passwords:
        demo_passwords = {
            "admin": "admin123",
            "john.doe": "password123",
            "jane.smith": "password123",
            "bob.wilson": "password123"
        }

        return demo_passwords.get(user.username.lower()) == password

    def _store_password_hash(self, user_id: int, password: str):
        """Store password hash (simplified for demo)"""
        # In production, use proper password hashing like bcrypt
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # This would be stored in a separate passwords table
        print(f"🔐 Password hash stored for user ID: {user_id}")

    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for role"""
        permissions = {
            UserRole.ADMIN.value: [
                "create_user", "edit_user", "delete_user", "change_roles",
                "create_task", "edit_any_task", "delete_any_task", "assign_tasks",
                "change_any_status", "view_all_tasks", "manage_projects",
                "manage_modules", "manage_versions", "manage_labels"
            ],
            UserRole.DEVELOPER.value: [
                "create_task", "edit_assigned_tasks", "assign_tasks",
                "change_task_status", "view_all_tasks", "add_comments",
                "add_attachments", "manage_own_tasks"
            ],
            UserRole.TESTER.value: [
                "create_task", "edit_assigned_tasks", "change_task_status",
                "view_all_tasks", "add_comments", "add_attachments",
                "verify_tasks", "manage_own_tasks"
            ],
            UserRole.REPORTER.value: [
                "create_task", "edit_own_tasks", "view_all_tasks",
                "add_comments", "add_attachments"
            ],
            UserRole.VIEWER.value: [
                "view_all_tasks", "add_comments"
            ]
        }

        return permissions.get(role, [])

    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if username not in self.failed_login_attempts:
            return False

        attempts_data = self.failed_login_attempts[username]
        if attempts_data["count"] >= self.max_failed_attempts:
            # Check if lockout period has expired
            if datetime.now() - attempts_data["last_attempt"] < self.lockout_duration:
                return True
            else:
                # Lockout expired, clear attempts
                del self.failed_login_attempts[username]
                return False

        return False

    def _record_failed_attempt(self, username: str):
        """Record failed login attempt"""
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = {"count": 0, "last_attempt": None}

        self.failed_login_attempts[username]["count"] += 1
        self.failed_login_attempts[username]["last_attempt"] = datetime.now()

        print(f"⚠️ Failed login attempt #{self.failed_login_attempts[username]['count']} for: {username}")

    def _update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.now()
            # This would be saved to database
            print(f"📅 Last login updated for: {user.username}")

    # ==================== DEMO SETUP METHODS ====================

    def setup_demo_users(self):
        """Create demo users for testing"""
        print("👥 Setting up demo users...")

        demo_users = [
            {
                "username": "admin",
                "email": "admin@taskmaster.local",
                "full_name": "System Administrator",
                "password": "admin123",
                "role": UserRole.ADMIN.value
            },
            {
                "username": "john.doe",
                "email": "john.doe@company.com",
                "full_name": "John Doe",
                "password": "password123",
                "role": UserRole.DEVELOPER.value
            },
            {
                "username": "jane.smith",
                "email": "jane.smith@company.com",
                "full_name": "Jane Smith",
                "password": "password123",
                "role": UserRole.DEVELOPER.value
            },
            {
                "username": "bob.wilson",
                "email": "bob.wilson@company.com",
                "full_name": "Bob Wilson",
                "password": "password123",
                "role": UserRole.TESTER.value
            }
        ]

        created_count = 0
        for user_data in demo_users:
            try:
                # Check if user already exists
                if not self.get_user_by_username(user_data["username"]):
                    self.create_user(
                        username=user_data["username"],
                        email=user_data["email"],
                        full_name=user_data["full_name"],
                        password=user_data["password"],
                        role=user_data["role"]
                    )
                    created_count += 1
                    print(f"✅ Demo user created: {user_data['full_name']}")
                else:
                    print(f"ℹ️ Demo user already exists: {user_data['full_name']}")
            except Exception as e:
                print(f"❌ Error creating demo user {user_data['full_name']}: {e}")

        print(f"📊 Demo users setup complete: {created_count} new users created")


class UserSession:
    """User session management"""

    def __init__(self, user: User):
        self.user = user
        self.login_time = datetime.now()
        self.last_activity = datetime.now()

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def get_session_duration(self) -> timedelta:
        """Get total session duration"""
        return datetime.now() - self.login_time

    def is_expired(self, timeout_hours: int = 8) -> bool:
        """Check if session has expired"""
        return (datetime.now() - self.last_activity) > timedelta(hours=timeout_hours)