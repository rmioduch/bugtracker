# TaskMaster Enhanced - Bug Tracker for Money Mentor AI

Professional bug tracking and task management system specifically designed for Money Mentor AI development. Built with Python and Tkinter, featuring a modern dark UI and comprehensive issue tracking capabilities.

## 🚀 Features

### Core Functionality
- 🐛 **Advanced Bug Tracking** - Complete issue lifecycle management
- 👥 **User Management** - Role-based access control (Admin, Developer, Tester, Reporter, Viewer)
- 📊 **Interactive Dashboard** - Real-time metrics and analytics
- 📋 **Multi-View Interface** - Dashboard, Kanban board, and list views
- 🔐 **Authentication System** - Secure login with user sessions
- 📁 **Project Organization** - Manage multiple projects simultaneously

### Bug Tracking Features
- **Issue Types**: Bug, Feature Request, Enhancement, Task, Documentation, Performance, Security, Refactoring
- **Priority Levels**: Critical (P0), High (P1), Medium (P2), Low (P3), Trivial (P4)
- **Severity Levels**: Blocker, Major, Minor, Trivial
- **Module Assignment**: 15+ predefined modules for Money Mentor AI
- **Version Tracking**: Affected version and fix version management
- **Reproduction Details**: Environment, steps to reproduce, expected/actual results
- **Time Tracking**: Estimated hours and time spent
- **Label System**: Customizable labels for categorization
- **Comments & Activity**: Full history tracking with timestamps

### UI Features
- 🌙 **Dark Theme** - Professional soft dark color scheme
- 📈 **Real-time Charts** - Visual analytics with pie and bar charts
- 🔍 **Quick Filters** - Instant filtering by various criteria
- 💾 **Auto-save** - Changes persist immediately
- 🖱️ **Drag & Drop** - Intuitive task management (Kanban view)
- 📱 **Responsive Design** - Adapts to different screen sizes

## 📸 Screenshots

![Login Screen](screenshots/login.png)
*Secure login with role-based access*

![Dashboard View](screenshots/dashboard.png)
*Interactive dashboard with real-time metrics*

![Task Details](screenshots/task_details.png)
*Comprehensive task/bug details with tabbed interface*

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11, macOS, or Linux
- No additional dependencies required (uses Python standard library)

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/taskmaster-bugtracker.git
cd taskmaster-bugtracker
```

2. **Run the application:**
```bash
python main.py
```

3. **Default login credentials:**
   - Username: `admin`
   - Password: `admin123`

### First Run

On first run, the application will:
1. Create necessary directories
2. Initialize the SQLite database
3. Create demo users
4. Set up default data (modules, labels, statuses)

## 🔧 Building Standalone Executable

### Windows (.exe)

1. **Install PyInstaller:**
```bash
pip install pyinstaller
```

2. **Create the executable:**
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="TaskMaster BugTracker" main.py
```

3. **Find your executable:**
   - Location: `dist/TaskMaster BugTracker.exe`
   - Copy to desktop for easy access

### Advanced Build Options

For a more optimized build with custom settings:

```bash
pyinstaller taskmaster.spec
```

See `taskmaster.spec` file for advanced configuration.

## 📚 Usage Guide

### User Roles

1. **Admin** - Full system access, user management
2. **Developer** - Create/edit tasks, assign to others
3. **Tester** - Create/edit tasks, verify fixes
4. **Reporter** - Create tasks, edit own tasks
5. **Viewer** - Read-only access

### Creating a Bug Report

1. Click "🐛 New Bug" in the toolbar
2. Fill in required fields:
   - Title (required)
   - Project (required)
   - Priority and Severity
   - Module affected
   - Description
3. Add reproduction steps in the "Reproduction" tab
4. Click "Create Issue"

### Managing Tasks

- **View Details**: Click any task in the dashboard
- **Edit**: Open task and modify fields
- **Comment**: Add comments in the Activity tab
- **Change Status**: Update status dropdown or drag in Kanban view
- **Assign**: Select assignee from user list

### Dashboard Analytics

The dashboard shows:
- Total issues count
- Open vs closed issues
- Critical bugs count
- Personal assignments
- Issues by module (pie chart)
- Issues by priority (bar chart)
- Recent activity feed

### Quick Filters

Use quick filters for common queries:
- 👤 My Issues
- 🐛 All Bugs
- 🔴 Critical Issues
- 📈 Trading Module
- 🔓 Open Issues
- 📅 Recent Activity

## 📁 Project Structure

```
taskmaster-bugtracker/
├── main.py                           # Application entry point
├── models/                           # Data models and database
│   ├── database.py                   # SQLite database manager
│   └── entities.py                   # Enhanced data classes
├── views/                            # User interface
│   ├── enhanced_main_window.py       # Main application window
│   ├── enhanced_task_dialog.py       # Task creation/editing dialog
│   ├── login_dialog.py               # Authentication dialog
│   ├── project_dialog.py             # Project management
│   └── user_management_dialog.py     # User administration
├── controllers/                      # Business logic
│   ├── task_controller.py            # Enhanced task operations
│   ├── project_controller.py         # Project operations
│   ├── user_controller.py            # User management
│   └── bug_dashboard_controller.py   # Dashboard logic
└── utils/                            # Utility functions
    └── helpers.py                    # Helper functions
```

## 🗄️ Database Schema

Enhanced schema with bug tracking tables:

- **users** - User accounts and roles
- **projects** - Project information
- **tasks** - Enhanced with bug tracking fields
- **modules** - System modules/components
- **versions** - Software versions
- **labels** - Customizable tags
- **comments** - Task discussions
- **attachments** - File attachments metadata
- **notifications** - User notifications
- **status_history** - Audit trail

## ⌨️ Keyboard Shortcuts

- `Enter` - Confirm dialog/login
- `Escape` - Cancel dialog
- `Tab` - Navigate between fields
- `Ctrl+S` - Save (in dialogs)
- `F5` - Refresh current view

## 🔧 Configuration

### Database Location

- **Windows**: `%APPDATA%/TaskMaster/taskmaster.db`
- **macOS**: `~/Library/Application Support/TaskMaster/taskmaster.db`
- **Linux**: `~/.config/TaskMaster/taskmaster.db`

### Backup & Restore

**Backup:**
```bash
python main.py --backup
```

**Restore:**
```bash
python main.py --restore backup_file.db
```

**Reset Database:**
```bash
python main.py --reset-db
```

## 🚀 Development

### Running in Development Mode

```bash
# Clone repository
git clone https://github.com/yourusername/taskmaster-bugtracker.git
cd taskmaster-bugtracker

# Run application
python main.py
```

### Code Style

- **PEP 8** compliant
- **Type hints** throughout
- **Comprehensive docstrings**
- **Error handling** with try/except blocks
- **Logging** for debugging

### Adding New Features

1. **Data Model**: Update `models/entities.py`
2. **Database**: Modify schema in `models/database.py`
3. **Business Logic**: Add to appropriate controller
4. **UI**: Create/update views in `views/`
5. **Test**: Ensure all features work correctly

## 🐛 Troubleshooting

### Common Issues

1. **"Enhanced Task Dialog is not available"**
   - Ensure all files are in correct directories
   - Check Python path configuration

2. **Database errors**
   - Try resetting: `python main.py --reset-db`
   - Check file permissions

3. **UI scaling issues**
   - Application auto-detects high DPI displays
   - Manual scaling available in settings

### Debug Mode

Run with debug output:
```bash
python main.py --debug
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 🗺️ Roadmap

### Version 2.1
- [ ] Email notifications
- [ ] Advanced search with filters
- [ ] Bulk operations
- [ ] Custom workflows

### Version 2.2
- [ ] REST API
- [ ] Webhook integrations
- [ ] Custom fields
- [ ] Report generation (PDF/Excel)

### Version 3.0
- [ ] Web interface
- [ ] Mobile apps
- [ ] Real-time collaboration
- [ ] AI-powered bug detection

## 📝 Changelog

### Version 2.0.0 (2025-12-XX)
- Complete rewrite with bug tracking focus
- User authentication and roles
- Enhanced dashboard with analytics
- Module-based organization
- Time tracking capabilities
- Label system
- Advanced filtering

### Version 1.0.0
- Initial task management system
- Basic Kanban board
- SQLite integration

## 🙏 Acknowledgments

- Designed specifically for Money Mentor AI development team
- Built with Python and Tkinter
- Icons from Unicode emoji set
- Color scheme inspired by modern developer tools

---

**Made with ❤️ for efficient bug tracking and task management**

For support, email: support@taskmaster.example.com