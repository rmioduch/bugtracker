#!/usr/bin/env python3
"""
TaskMaster Enhanced - Personal Task Management & Bug Tracker Application
UPROSZCZONA WERSJA - bez skomplikowanych migracji
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import enhanced components
try:
    from models.database import DatabaseManager
    from views.enhanced_main_window import EnhancedMainWindow
    from controllers.user_controller import UserController
    from utils.helpers import get_app_data_dir
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required files are in place.")
    sys.exit(1)


class TaskMasterApp:
    """Uproszczona aplikacja TaskMaster Enhanced - bez migracji"""

    def __init__(self):
        self.root = None
        self.db_manager = None
        self.user_controller = None
        self.main_window = None

        # Application info
        self.app_name = "TaskMaster Enhanced"
        self.version = "2.0.0"
        self.description = "Bug Tracker for Money Mentor AI"

    def initialize(self):
        """Initialize the application"""
        try:
            print("=" * 60)
            print(f"🚀 Starting {self.app_name} v{self.version}")
            print(f"📝 {self.description}")
            print("=" * 60)

            # Step 1: Initialize Tkinter
            self._initialize_tkinter()

            # Step 2: Setup database (SIMPLE VERSION)
            self._setup_simple_database()

            # Step 3: Initialize controllers
            self._initialize_controllers()

            # Step 4: Setup demo data
            self._setup_demo_data()

            # Step 5: Create main window
            self._create_main_window()

            print("✅ Application initialized successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize application: {e}")
            import traceback
            traceback.print_exc()
            self._show_error("Initialization Error",
                             f"Failed to start {self.app_name}:\n\n{str(e)}")
            return False

    def _initialize_tkinter(self):
        """Initialize Tkinter root window"""
        print("🎨 Initializing UI framework...")

        self.root = tk.Tk()
        self.root.withdraw()  # Hide initially

        # Set basic window properties
        self.root.title(f"{self.app_name} v{self.version}")

        print("✅ UI framework initialized")

    def _setup_simple_database(self):
        """Setup database - SIMPLE VERSION without migration"""
        print("🗄️ Setting up database (simple mode)...")

        # Determine database path
        app_data_dir = get_app_data_dir()
        db_path = os.path.join(app_data_dir, "taskmaster.db")

        print(f"📍 Database location: {db_path}")

        # SIMPLE: Check if we want to reset database
        if os.path.exists(db_path):
            print("📋 Found existing database")

            # Ask user if they want to start fresh
            response = messagebox.askyesno(
                "Database Found",
                "Found existing database. Do you want to:\n\n"
                "YES = Keep existing data\n"
                "NO = Start with fresh empty database\n\n"
                "Choose NO if you're having problems with the database.",
                icon='question'
            )

            if not response:  # User chose NO = fresh start
                print("🗑️ User chose to start fresh - removing old database")
                try:
                    # Create backup first
                    backup_path = f"{db_path}.backup_{int(datetime.now().timestamp())}"
                    shutil.copy2(db_path, backup_path)
                    print(f"📁 Backup created: {backup_path}")

                    # Remove old database
                    os.remove(db_path)
                    print("✅ Old database removed")
                except Exception as e:
                    print(f"⚠️ Could not remove old database: {e}")

        # Initialize database manager
        print("🔧 Creating database manager...")
        self.db_manager = DatabaseManager(db_path)

        print("📋 Initializing database tables...")
        self.db_manager.initialize_database()

        print("✅ Database ready")

    def _initialize_controllers(self):
        """Initialize application controllers"""
        print("🎮 Initializing controllers...")

        # IMPORTANT: Pass database manager to user controller
        self.user_controller = UserController(self.db_manager)

        print("✅ Controllers initialized")

    def _setup_demo_data(self):
        """Setup demo data if needed"""
        print("📊 Setting up demo data...")

        try:
            # Setup demo users (database manager already passed in constructor)
            self.user_controller.setup_demo_users()

            print("✅ Demo data ready")

        except Exception as e:
            print(f"⚠️ Demo data warning: {e}")
            import traceback
            traceback.print_exc()
            # Demo data is not critical, continue anyway

    def _create_main_window(self):
        """Create and show main application window"""
        print("🖼️ Creating main window...")

        try:
            self.main_window = EnhancedMainWindow(self.root)
            print("✅ Main window created")

        except Exception as e:
            print(f"❌ Failed to create main window: {e}")
            import traceback
            traceback.print_exc()
            raise

    def run(self):
        """Run the application"""
        try:
            if not self.initialize():
                return False

            print("🎯 Starting application main loop...")

            # Show root window
            self.root.deiconify()

            # Start main event loop
            self.root.mainloop()

            print("👋 Application closed")
            return True

        except KeyboardInterrupt:
            print("\n⚠️ Application interrupted by user")
            return False

        except Exception as e:
            print(f"❌ Runtime error: {e}")
            import traceback
            traceback.print_exc()
            self._show_error("Runtime Error", f"An error occurred:\n\n{str(e)}")
            return False

        finally:
            self._cleanup()

    def _cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")

        try:
            if self.db_manager:
                self.db_manager.close_connection()

            if self.user_controller:
                self.user_controller.logout_user()

        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

        print("✅ Cleanup completed")

    def _show_error(self, title: str, message: str):
        """Show error message to user"""
        try:
            if self.root:
                messagebox.showerror(title, message)
            else:
                print(f"ERROR: {title} - {message}")
        except:
            print(f"ERROR: {title} - {message}")


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False

    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """Check if all required modules are available"""
    required_modules = [
        'tkinter',
        'sqlite3',
        'datetime',
        'typing',
        'dataclasses'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        return False

    print("✅ All required modules available")
    return True


def create_app_directories():
    """Create necessary application directories"""
    try:
        app_data_dir = get_app_data_dir()

        # Create subdirectories
        subdirs = ['logs', 'backups', 'exports', 'attachments']

        for subdir in subdirs:
            subdir_path = os.path.join(app_data_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)

        print(f"✅ Application directories created in: {app_data_dir}")
        return True

    except Exception as e:
        print(f"⚠️ Could not create app directories: {e}")
        return False


def show_startup_banner():
    """Show application startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🐛 TaskMaster Enhanced - Bug Tracker Edition             ║
║                                                              ║
║   📋 Professional Task Management & Bug Tracking            ║
║   🎯 Designed for Money Mentor AI Development               ║
║                                                              ║
║   Features:                                                  ║
║   • Advanced Bug Tracking                                   ║
║   • User Management & Roles                                 ║
║   • Project Organization                                    ║
║   • Dashboard Analytics                                     ║
║   • Kanban Boards                                          ║
║   • Multi-view Interface                                   ║
║                                                              ║
║   Version: 2.0.0 (Simple Mode)                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def reset_database_if_needed():
    """Utility function to reset database if user wants"""
    app_data_dir = get_app_data_dir()
    db_path = os.path.join(app_data_dir, "taskmaster.db")

    if "--reset-db" in sys.argv:
        print("🗑️ Resetting database (--reset-db flag detected)...")

        if os.path.exists(db_path):
            # Create backup
            backup_path = f"{db_path}.backup_{int(datetime.now().timestamp())}"
            shutil.copy2(db_path, backup_path)
            print(f"📁 Backup created: {backup_path}")

            # Remove database
            os.remove(db_path)
            print("✅ Database reset completed")
        else:
            print("ℹ️ No database found to reset")


def main():
    """Main application entry point"""
    try:
        # Show startup banner
        show_startup_banner()

        # Handle reset database flag
        reset_database_if_needed()

        # Pre-flight checks
        print("🔍 Running pre-flight checks...")

        if not check_python_version():
            input("Press Enter to exit...")
            sys.exit(1)

        if not check_dependencies():
            input("Press Enter to exit...")
            sys.exit(1)

        if not create_app_directories():
            print("⚠️ Warning: Could not create application directories")

        print("✅ Pre-flight checks completed")
        print()

        # Create and run application
        app = TaskMasterApp()
        success = app.run()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        sys.exit(130)  # Standard exit code for Ctrl+C

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print(f"Error type: {type(e).__name__}")

        # Show error details
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()

        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ["--help", "-h"]:
            print("TaskMaster Enhanced v2.0.0 - Bug Tracker Edition")
            print("Usage: python main.py [--reset-db] [--help]")
            sys.exit(0)

        elif arg in ["--version", "-v"]:
            print("TaskMaster Enhanced v2.0.0 (Simple Mode)")
            sys.exit(0)

    # Run main application
    main()