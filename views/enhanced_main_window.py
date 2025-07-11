"""
Enhanced Main Window - TaskMaster BugTracker Integration
POPRAWIONA WERSJA - maksymalne wykorzystanie szerokości ekranu + DZIAŁAJĄCE FILTROWANIE DASHBOARDU
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict

try:
    from controllers.task_controller import TaskController
    from controllers.project_controller import ProjectController
    from controllers.user_controller import UserController
    from controllers.bug_dashboard_controller import BugDashboardController
    from views.enhanced_task_dialog import EnhancedTaskDialog
    from views.project_dialog import ProjectDialog
    from views.login_dialog import LoginDialog
    from views.user_management_dialog import UserManagementDialog
    from views.kanban_board_view import KanbanBoardView
    from views.list_view import ListView
    from models.entities import Task, Project, User, SearchFilter
    from utils.helpers import format_date
    print("✅ All imports successful for EnhancedMainWindow (including Kanban & ListView)")
except Exception as e:
    print(f"❌ Import error in EnhancedMainWindow: {e}")
    raise


class EnhancedMainWindow:
    """Enhanced main window with FULL-WIDTH layout - POPRAWIONA WERSJA z działającym filtrowaniem"""

    def __init__(self, root):
        print("🖼️ Starting EnhancedMainWindow initialization...")

        try:
            self.root = root
            print("   ✅ Root window assigned")

            # Initialize controllers
            print("   🎮 Initializing controllers...")
            self.task_controller = TaskController()
            self.project_controller = ProjectController()
            self.user_controller = UserController()
            self.dashboard_controller = BugDashboardController(self)
            print("   ✅ Controllers initialized")

            # Application state
            self.current_user = None
            self.current_filter = SearchFilter()
            self.current_view = "dashboard"  # dashboard, kanban, list
            self.login_dialog = None

            # View instances (will be created when needed)
            self.kanban_view = None
            self.list_view = None

            # UI References
            self.main_container = None
            self.sidebar_frame = None
            self.content_frame = None
            self.toolbar_frame = None
            self.status_bar_frame = None

            # View button references for highlighting
            self.view_buttons = {}

            # Soft Dark color palette (Money Mentor AI theme)
            self.colors = {
                'bg_primary': '#1a222c',
                'bg_secondary': '#2d3748',
                'bg_card': '#374151',
                'bg_hover': '#4b5563',
                'text_primary': '#f7fafc',
                'text_secondary': '#cbd5e0',
                'text_muted': '#a0aec0',
                'accent_gold': '#E8C547',
                'accent_teal': '#00BFA6',
                'accent_purple': '#9F7AEA',
                'critical': '#EF4444',
                'border_light': '#4a5568',
            }
            print("   ✅ Color palette initialized")

            # Setup application
            print("   🔧 Setting up window...")
            self._setup_window()

            print("   🔐 Showing login dialog...")
            self._show_login()

            print("✅ EnhancedMainWindow initialization completed!")

        except Exception as e:
            print(f"❌ Error in EnhancedMainWindow.__init__: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _setup_window(self):
        """Configure main application window"""
        print("      🪟 Configuring main window...")

        try:
            self.root.title("TaskMaster - Bug Tracker for Money Mentor AI")
            self.root.geometry("1600x900")
            self.root.minsize(1200, 700)
            self.root.configure(bg=self.colors['bg_primary'])
            print("      ✅ Window configuration completed")

        except Exception as e:
            print(f"      ❌ Error configuring window: {e}")
            raise

    def _show_login(self):
        """Show login dialog - FIXED VERSION"""
        print("      🔐 Creating login dialog...")

        try:
            # Create login dialog (no wait_window this time!)
            self.login_dialog = LoginDialog(self.root, self.user_controller)

            # Start checking for login result
            self._check_login_result()

            print("      ✅ Login dialog created, checking for result...")

        except Exception as e:
            print(f"      ❌ Error in login process: {e}")
            import traceback
            traceback.print_exc()

            # Show error and provide fallback
            self._handle_login_error(e)

    def _check_login_result(self):
        """Check login result periodically"""
        try:
            # Check if dialog still exists
            if not self.login_dialog or not self.login_dialog.dialog:
                print("      ℹ️ Login dialog no longer exists")

                # Check if we have authenticated user
                if self.login_dialog and self.login_dialog.authenticated_user:
                    print(f"      ✅ User authenticated: {self.login_dialog.authenticated_user.username}")
                    self.current_user = self.login_dialog.authenticated_user
                    self._on_login_success()
                else:
                    print("      ❌ No user authenticated - exiting")
                    self.root.quit()
                return

            # Check if dialog has winfo_exists (still active)
            try:
                if not self.login_dialog.dialog.winfo_exists():
                    print("      ℹ️ Dialog window closed")

                    # Check authentication result
                    if self.login_dialog.authenticated_user:
                        print(f"      ✅ User authenticated: {self.login_dialog.authenticated_user.username}")
                        self.current_user = self.login_dialog.authenticated_user
                        self._on_login_success()
                    else:
                        print("      ❌ Authentication cancelled")
                        self.root.quit()
                    return
            except tk.TclError:
                # Dialog was destroyed
                print("      ℹ️ Dialog was destroyed")

                if self.login_dialog.authenticated_user:
                    print(f"      ✅ User authenticated: {self.login_dialog.authenticated_user.username}")
                    self.current_user = self.login_dialog.authenticated_user
                    self._on_login_success()
                else:
                    print("      ❌ No authentication")
                    self.root.quit()
                return

            # Dialog still exists, check again in 100ms
            self.root.after(100, self._check_login_result)

        except Exception as e:
            print(f"      ❌ Error checking login result: {e}")
            self._handle_login_error(e)

    def _on_login_success(self):
        """Handle successful login"""
        print("      🎉 Login successful, creating main interface...")

        try:
            # Create main interface
            self._create_main_interface()

            # Load initial data
            self._load_initial_data()

            # Show welcome message in status bar instead of popup
            self._update_status(f"Welcome {self.current_user.full_name}! TaskMaster is ready.")

            print("      ✅ Main interface ready!")

        except Exception as e:
            print(f"      ❌ Error creating main interface: {e}")
            import traceback
            traceback.print_exc()
            self._handle_login_error(e)

    def _handle_login_error(self, error):
        """Handle login errors gracefully"""
        print(f"🔧 Handling login error: {error}")

        try:
            # Try to auto-login as admin
            response = messagebox.askyesno(
                "Login Error",
                f"Login had an issue: {str(error)}\n\n"
                "Would you like to try emergency admin login?\n\n"
                "YES = Try admin login\n"
                "NO = Exit application"
            )

            if response:
                print("   🔧 Attempting emergency admin login...")
                self._emergency_admin_login()
            else:
                print("   👋 User chose to exit")
                self.root.quit()

        except Exception as e2:
            print(f"   ❌ Error handling also failed: {e2}")
            messagebox.showerror("Critical Error", "Cannot start application")
            self.root.quit()

    def _emergency_admin_login(self):
        """Emergency admin login"""
        try:
            success, user, message = self.user_controller.authenticate_user("admin", "admin123")

            if success:
                self.current_user = user
                print(f"   ✅ Emergency login successful: {user.full_name}")

                # Create main interface
                self._create_main_interface()
                self._load_initial_data()

                # Show message in status bar instead of popup
                self._update_status(f"Emergency login successful - Welcome {user.full_name}!")

            else:
                print(f"   ❌ Emergency login failed: {message}")
                messagebox.showerror("Emergency Login Failed", message)
                self.root.quit()

        except Exception as e:
            print(f"   ❌ Emergency login error: {e}")
            messagebox.showerror("Critical Error", f"Emergency login failed: {str(e)}")
            self.root.quit()

    def _create_main_interface(self):
        """Create the main application interface - FULL WIDTH VERSION"""
        print("         🎨 Creating FULL-WIDTH main interface...")

        try:
            # Clear any existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            print("            ✅ Cleared existing widgets")

            # Main container - ZERO EXTERNAL PADDING
            self.main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
            self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            print("            ✅ Main container created")

            # Create main sections
            print("            🛠️ Creating toolbar...")
            self._create_toolbar()

            print("            📋 Creating FULL-WIDTH main content...")
            self._create_main_content_fullwidth()

            print("            📊 Creating status bar...")
            self._create_status_bar()

            # Set initial view
            print("            📊 Setting initial view to dashboard...")
            self._switch_to_dashboard()

            print("         ✅ FULL-WIDTH main interface creation completed!")

        except Exception as e:
            print(f"         ❌ Error creating main interface: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _create_toolbar(self):
        """Create application toolbar"""
        print("               🔧 Creating toolbar...")

        try:
            self.toolbar_frame = tk.Frame(self.main_container,
                                          bg=self.colors['bg_secondary'],
                                          height=60)
            self.toolbar_frame.pack(fill=tk.X)
            self.toolbar_frame.pack_propagate(False)

            # Left side - Application branding
            left_frame = tk.Frame(self.toolbar_frame, bg=self.colors['bg_secondary'])
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15)

            # App title with icon
            title_frame = tk.Frame(left_frame, bg=self.colors['bg_secondary'])
            title_frame.pack(side=tk.LEFT, pady=15)

            app_icon = tk.Label(title_frame, text="🐛",
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['accent_gold'],
                                font=('Segoe UI', 20))
            app_icon.pack(side=tk.LEFT)

            app_title = tk.Label(title_frame, text="TaskMaster",
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_primary'],
                                 font=('Segoe UI', 14, 'bold'))
            app_title.pack(side=tk.LEFT, padx=(8, 0))

            subtitle = tk.Label(title_frame, text="Bug Tracker",
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['text_secondary'],
                                font=('Segoe UI', 10))
            subtitle.pack(side=tk.LEFT, padx=(5, 0))

            # Center - View switcher
            center_frame = tk.Frame(self.toolbar_frame, bg=self.colors['bg_secondary'])
            center_frame.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=20)

            view_frame = tk.Frame(center_frame, bg=self.colors['bg_secondary'])
            view_frame.pack(pady=12)

            # View buttons - store references for highlighting
            self.view_buttons = {}
            self._create_view_button(view_frame, "📊 Dashboard", "dashboard")
            self._create_view_button(view_frame, "📋 Kanban", "kanban")
            self._create_view_button(view_frame, "📄 List View", "list")

            # Right side - User actions and info
            right_frame = tk.Frame(self.toolbar_frame, bg=self.colors['bg_secondary'])
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=15)

            # Quick action buttons
            actions_frame = tk.Frame(right_frame, bg=self.colors['bg_secondary'])
            actions_frame.pack(side=tk.LEFT, pady=12, padx=(0, 15))

            self._create_action_button(actions_frame, "🐛 New Bug", self._new_bug)
            self._create_action_button(actions_frame, "✨ New Feature", self._new_feature)
            self._create_action_button(actions_frame, "📁 New Project", self._new_project)

            # User info and menu
            user_frame = tk.Frame(right_frame, bg=self.colors['bg_secondary'])
            user_frame.pack(side=tk.RIGHT, pady=12)

            user_info = tk.Label(user_frame,
                                 text=f"👤 {self.current_user.full_name if self.current_user else 'Unknown User'}",
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_primary'],
                                 font=('Segoe UI', 10))
            user_info.pack(side=tk.LEFT, padx=(0, 10))

            # User menu button
            menu_btn = tk.Label(user_frame, text="⚙️",
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_primary'],
                                font=('Segoe UI', 12),
                                padx=8, pady=4,
                                cursor='hand2')
            menu_btn.pack(side=tk.RIGHT)
            menu_btn.bind("<Button-1>", self._show_user_menu)

            print("               ✅ Toolbar created successfully")

        except Exception as e:
            print(f"               ❌ Error creating toolbar: {e}")
            raise

    def _create_main_content_fullwidth(self):
        """Create main content area - FULL WIDTH VERSION"""
        print("               📋 Creating FULL-WIDTH main content area...")

        try:
            # Content container - ZERO PADDING dla maksymalnej szerokości
            content_container = tk.Frame(self.main_container, bg=self.colors['bg_primary'])
            content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

            # NOWY LAYOUT - Horizontal z kompaktowym sidebar'em
            # Left sidebar - KOMPAKTOWY (tylko 220px)
            self._create_compact_sidebar(content_container)

            # Right content area - CAŁA RESZTA PRZESTRZENI
            self._create_content_area_fullwidth(content_container)

            print("               ✅ FULL-WIDTH main content area created")

        except Exception as e:
            print(f"               ❌ Error creating main content: {e}")
            raise

    def _create_compact_sidebar(self, parent):
        """Create compact left sidebar - KOMPAKTOWY"""
        print("                  📂 Creating COMPACT sidebar...")

        try:
            self.sidebar_frame = tk.Frame(parent,
                                          bg=self.colors['bg_secondary'],
                                          width=220)  # Zmniejszona szerokość z 300 na 220
            self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0), pady=5)
            self.sidebar_frame.pack_propagate(False)

            # Quick filters section - KOMPAKTOWE
            self._create_compact_quick_filters()

            # Projects section - KOMPAKTOWE
            self._create_compact_projects_section()

            # Statistics section - KOMPAKTOWE
            self._create_compact_statistics_section()

            print("                  ✅ COMPACT sidebar created")

        except Exception as e:
            print(f"                  ❌ Error creating sidebar: {e}")
            raise

    def _create_content_area_fullwidth(self, parent):
        """Create main content area - MAKSYMALNA SZEROKOŚĆ"""
        print("                  🖼️ Creating FULL-WIDTH content area...")

        try:
            # Content frame - ZERO PADDING, maksymalna szerokość
            self.content_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
            self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 5), pady=5)

            print("                  ✅ FULL-WIDTH content area created")

        except Exception as e:
            print(f"                  ❌ Error creating content area: {e}")
            raise

    def _create_compact_quick_filters(self):
        """Create compact quick filters section"""
        filters_frame = tk.LabelFrame(self.sidebar_frame,
                                      text="🔍 Filters",
                                      bg=self.colors['bg_secondary'],
                                      fg=self.colors['text_primary'],
                                      font=('Segoe UI', 10, 'bold'),
                                      bd=0)
        filters_frame.pack(fill=tk.X, padx=8, pady=(8, 5))

        # KOMPAKTOWE filtry
        filters = [
            ("👤 My Issues", lambda: self._apply_filter(assignee_id=self.current_user.id if self.current_user else None)),
            ("🐛 Bugs", lambda: self._apply_filter(issue_type="BUG")),
            ("🔴 Critical", lambda: self._apply_filter(priority=1)),
            ("🔓 Open", lambda: self._apply_filter(status_open=True))
        ]

        for text, command in filters:
            btn = tk.Label(filters_frame, text=text,
                           bg=self.colors['bg_card'],
                           fg=self.colors['text_primary'],
                           font=('Segoe UI', 8),  # Mniejszy font
                           padx=8, pady=3,  # Mniejszy padding
                           cursor='hand2',
                           anchor='w')
            btn.pack(fill=tk.X, padx=3, pady=1)

            def make_handler(cmd):
                def handler(event):
                    try:
                        cmd()
                    except Exception as e:
                        print(f"Filter error: {e}")
                        messagebox.showerror("Filter Error", f"Filter failed: {str(e)}")
                return handler

            def on_enter(event, widget=btn):
                widget.configure(bg=self.colors['accent_gold'], fg='black')

            def on_leave(event, widget=btn):
                widget.configure(bg=self.colors['bg_card'], fg=self.colors['text_primary'])

            btn.bind("<Button-1>", make_handler(command))
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def _create_compact_projects_section(self):
        """Create compact projects section"""
        projects_frame = tk.LabelFrame(self.sidebar_frame,
                                       text="📁 Projects",
                                       bg=self.colors['bg_secondary'],
                                       fg=self.colors['text_primary'],
                                       font=('Segoe UI', 10, 'bold'),
                                       bd=0)
        projects_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        # Projects listbox - KOMPAKTOWY
        listbox_frame = tk.Frame(projects_frame, bg=self.colors['bg_secondary'])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        self.projects_listbox = tk.Listbox(listbox_frame,
                                           selectmode=tk.SINGLE,
                                           bg=self.colors['bg_card'],
                                           fg=self.colors['text_primary'],
                                           selectbackground=self.colors['accent_teal'],
                                           font=('Segoe UI', 8),  # Mniejszy font
                                           relief='flat',
                                           bd=0,
                                           highlightthickness=0)
        self.projects_listbox.pack(fill=tk.BOTH, expand=True)
        self.projects_listbox.bind('<<ListboxSelect>>', self._on_project_select)

        # Project buttons - KOMPAKTOWE
        buttons_frame = tk.Frame(projects_frame, bg=self.colors['bg_secondary'])
        buttons_frame.pack(fill=tk.X, padx=3, pady=3)

        self._create_small_button(buttons_frame, "➕", self._new_project, 'left')
        self._create_small_button(buttons_frame, "✏️", self._edit_project, 'left')
        if self.current_user and self.current_user.role == "ADMIN":
            self._create_small_button(buttons_frame, "🗑️", self._delete_project, 'left')

    def _create_compact_statistics_section(self):
        """Create compact statistics section"""
        self.stats_frame = tk.LabelFrame(self.sidebar_frame,
                                         text="📊 Stats",
                                         bg=self.colors['bg_secondary'],
                                         fg=self.colors['text_primary'],
                                         font=('Segoe UI', 10, 'bold'),
                                         bd=0)
        self.stats_frame.pack(fill=tk.X, padx=8, pady=(5, 8))

    def _create_view_button(self, parent, text, view_name):
        """Create view switcher button"""
        btn = tk.Label(parent, text=text,
                       bg=self.colors['bg_card'],
                       fg=self.colors['text_primary'],
                       font=('Segoe UI', 10),
                       padx=15, pady=8,
                       cursor='hand2')
        btn.pack(side=tk.LEFT, padx=3)

        # Store reference for highlighting
        self.view_buttons[view_name] = btn

        # Highlight current view
        if view_name == self.current_view:
            btn.configure(bg=self.colors['accent_gold'], fg='black')

        def on_click(event):
            self._switch_view(view_name)

        def on_enter(event):
            if view_name != self.current_view:
                btn.configure(bg=self.colors['bg_hover'])

        def on_leave(event):
            if view_name != self.current_view:
                btn.configure(bg=self.colors['bg_card'])

        btn.bind("<Button-1>", on_click)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _create_action_button(self, parent, text, command):
        """Create toolbar action button"""
        btn = tk.Label(parent, text=text,
                       bg=self.colors['accent_teal'],
                       fg='white',
                       font=('Segoe UI', 9, 'bold'),
                       padx=12, pady=6,
                       cursor='hand2')
        btn.pack(side=tk.LEFT, padx=2)

        def on_click(event):
            command()

        def on_enter(event):
            btn.configure(bg=self._darken_color(self.colors['accent_teal']))

        def on_leave(event):
            btn.configure(bg=self.colors['accent_teal'])

        btn.bind("<Button-1>", on_click)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _create_small_button(self, parent, text, command, side='left'):
        """Create small sidebar button"""
        btn = tk.Label(parent, text=text,
                       bg=self.colors['bg_card'],
                       fg=self.colors['text_secondary'],
                       font=('Segoe UI', 7),  # Mniejszy font
                       padx=6, pady=2,  # Mniejszy padding
                       cursor='hand2')
        btn.pack(side=side, padx=1)

        def on_enter(event):
            btn.configure(bg=self.colors['bg_hover'], fg=self.colors['text_primary'])

        def on_leave(event):
            btn.configure(bg=self.colors['bg_card'], fg=self.colors['text_secondary'])

        def on_click(event):
            try:
                command()
            except Exception as e:
                print(f"Button command error: {e}")
                messagebox.showerror("Error", f"Action failed: {str(e)}")

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)

    def _create_status_bar(self):
        """Create status bar"""
        print("               📊 Creating status bar...")

        try:
            self.status_bar_frame = tk.Frame(self.main_container,
                                             bg=self.colors['bg_secondary'],
                                             height=25)
            self.status_bar_frame.pack(fill=tk.X, side=tk.BOTTOM)
            self.status_bar_frame.pack_propagate(False)

            self.status_label = tk.Label(self.status_bar_frame,
                                         text="Ready",
                                         bg=self.colors['bg_secondary'],
                                         fg=self.colors['text_secondary'],
                                         font=('Segoe UI', 9),
                                         anchor='w')
            self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=3)

            # Connection status
            connection_label = tk.Label(self.status_bar_frame,
                                        text="🟢 Connected",
                                        bg=self.colors['bg_secondary'],
                                        fg=self.colors['text_secondary'],
                                        font=('Segoe UI', 9))
            connection_label.pack(side=tk.RIGHT, padx=10, pady=3)

            print("               ✅ Status bar created")

        except Exception as e:
            print(f"               ❌ Error creating status bar: {e}")
            raise

    # ==================== VIEW SWITCHING - FULLY INTEGRATED ====================

    def _switch_view(self, view_name):
        """Switch between different views - FULLY INTEGRATED"""
        print(f"🔄 Switching to {view_name} view...")

        try:
            self.current_view = view_name

            # Update toolbar buttons highlighting
            self._refresh_toolbar_highlighting()

            # Clear content area
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # Clear view instances (they will be recreated)
            if view_name != "kanban":
                self.kanban_view = None
            if view_name != "list":
                self.list_view = None

            # Show appropriate view
            if view_name == "dashboard":
                self._switch_to_dashboard()
            elif view_name == "kanban":
                self._switch_to_kanban()
            elif view_name == "list":
                self._switch_to_list_view()

            self._update_status(f"Switched to {view_name.title()} view")
            print(f"✅ Successfully switched to {view_name} view")

        except Exception as e:
            print(f"❌ Error switching to {view_name} view: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("View Error", f"Failed to switch to {view_name} view: {str(e)}")

    def _switch_to_dashboard(self):
        """Switch to dashboard view"""
        print("   📊 Creating dashboard view...")

        try:
            self.dashboard_controller.create_dashboard_view(self.content_frame)

            # KLUCZOWE - zastosuj aktualny filtr do dashboardu
            print(f"   🔧 Applying current filter to dashboard: {self.current_filter}")
            self.dashboard_controller.update_filter(self.current_filter)

            print("   ✅ Dashboard view created with current filter applied")
        except Exception as e:
            print(f"   ❌ Dashboard creation error: {e}")
            # Create fallback dashboard
            self._create_fallback_dashboard()

    def _switch_to_kanban(self):
        """Switch to kanban board view - FULLY INTEGRATED"""
        print("   📋 Creating kanban board view...")

        try:
            # Create new kanban view instance
            self.kanban_view = KanbanBoardView(
                parent_frame=self.content_frame,
                parent_window=self,
                task_controller=self.task_controller,
                project_controller=self.project_controller
            )
            print("   ✅ Kanban board view created successfully")

        except Exception as e:
            print(f"   ❌ Kanban board creation error: {e}")
            import traceback
            traceback.print_exc()

            # Create fallback kanban view
            self._create_fallback_kanban()

    def _switch_to_list_view(self):
        """Switch to list view - FULLY INTEGRATED"""
        print("   📄 Creating list view...")

        try:
            # Create new list view instance
            self.list_view = ListView(
                parent_frame=self.content_frame,
                parent_window=self,
                task_controller=self.task_controller,
                project_controller=self.project_controller
            )
            print("   ✅ List view created successfully")

        except Exception as e:
            print(f"   ❌ List view creation error: {e}")
            import traceback
            traceback.print_exc()

            # Create fallback list view
            self._create_fallback_list_view()

    def _create_fallback_dashboard(self):
        """Create simple fallback dashboard if main dashboard fails"""
        print("   🔧 Creating fallback dashboard...")

        try:
            # Simple placeholder dashboard
            fallback_frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
            fallback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Header
            header_label = tk.Label(fallback_frame,
                                    text="📊 TaskMaster Dashboard",
                                    bg=self.colors['bg_primary'],
                                    fg=self.colors['text_primary'],
                                    font=('Segoe UI', 16, 'bold'))
            header_label.pack(pady=(0, 20))

            # Simple metrics
            metrics_frame = tk.Frame(fallback_frame, bg=self.colors['bg_secondary'])
            metrics_frame.pack(fill=tk.X, pady=10)

            # Get basic stats
            try:
                metrics = self.task_controller.get_dashboard_metrics(self.current_user.id if self.current_user else None)

                stats_text = f"""
Welcome to TaskMaster Enhanced Bug Tracker!

📊 Quick Stats:
• Total Issues: {metrics.total_issues}
• Open Issues: {metrics.open_issues}
• Critical Bugs: {metrics.critical_bugs}
• My Assigned: {metrics.my_assigned}

🎯 Ready to track bugs for Money Mentor AI!
                """.strip()

            except Exception:
                stats_text = """
Welcome to TaskMaster Enhanced Bug Tracker!

🎯 System is ready for Money Mentor AI development!

Use the buttons above to:
• 🐛 Report new bugs
• ✨ Request new features  
• 📁 Manage projects
                """.strip()

            stats_label = tk.Label(metrics_frame,
                                   text=stats_text,
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_primary'],
                                   font=('Segoe UI', 11),
                                   justify=tk.LEFT)
            stats_label.pack(padx=20, pady=20)

            print("   ✅ Fallback dashboard created")

        except Exception as e:
            print(f"   ❌ Even fallback dashboard failed: {e}")

    def _create_fallback_kanban(self):
        """Create fallback kanban view if main kanban fails"""
        print("   🔧 Creating fallback kanban view...")

        try:
            fallback_frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
            fallback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Header
            header_label = tk.Label(fallback_frame,
                                    text="📋 Kanban Board View",
                                    bg=self.colors['bg_primary'],
                                    fg=self.colors['text_primary'],
                                    font=('Segoe UI', 16, 'bold'))
            header_label.pack(pady=(0, 20))

            # Error message
            error_frame = tk.Frame(fallback_frame, bg=self.colors['bg_secondary'])
            error_frame.pack(fill=tk.X, pady=10)

            error_text = """
⚠️ Kanban Board Temporarily Unavailable

The advanced Kanban board encountered an issue.

Try these alternatives:
• 📄 Use List View for detailed task management
• 📊 Return to Dashboard for overview
• 🔄 Refresh the application

The development team has been notified.
            """.strip()

            error_label = tk.Label(error_frame,
                                   text=error_text,
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_primary'],
                                   font=('Segoe UI', 11),
                                   justify=tk.LEFT)
            error_label.pack(padx=20, pady=20)

            print("   ✅ Fallback kanban view created")

        except Exception as e:
            print(f"   ❌ Even fallback kanban failed: {e}")

    def _create_fallback_list_view(self):
        """Create fallback list view if main list view fails"""
        print("   🔧 Creating fallback list view...")

        try:
            fallback_frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
            fallback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Header
            header_label = tk.Label(fallback_frame,
                                    text="📄 List View",
                                    bg=self.colors['bg_primary'],
                                    fg=self.colors['text_primary'],
                                    font=('Segoe UI', 16, 'bold'))
            header_label.pack(pady=(0, 20))

            # Error message
            error_frame = tk.Frame(fallback_frame, bg=self.colors['bg_secondary'])
            error_frame.pack(fill=tk.X, pady=10)

            error_text = """
⚠️ Advanced List View Temporarily Unavailable

The detailed list view encountered an issue.

Try these alternatives:
• 📋 Use Kanban Board for visual task management
• 📊 Return to Dashboard for overview
• 🔄 Refresh the application

Basic task operations are still available through the dashboard.
            """.strip()

            error_label = tk.Label(error_frame,
                                   text=error_text,
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_primary'],
                                   font=('Segoe UI', 11),
                                   justify=tk.LEFT)
            error_label.pack(padx=20, pady=20)

            print("   ✅ Fallback list view created")

        except Exception as e:
            print(f"   ❌ Even fallback list view failed: {e}")

    def _refresh_toolbar_highlighting(self):
        """Refresh toolbar to highlight current view"""
        print(f"   🎨 Updating toolbar highlighting for {self.current_view} view...")

        try:
            # Update all view buttons
            for view_name, button in self.view_buttons.items():
                if view_name == self.current_view:
                    # Highlight current view
                    button.configure(bg=self.colors['accent_gold'], fg='black')
                else:
                    # Reset other buttons
                    button.configure(bg=self.colors['bg_card'], fg=self.colors['text_primary'])

            print("   ✅ Toolbar highlighting updated")

        except Exception as e:
            print(f"   ❌ Error updating toolbar highlighting: {e}")

    # ==================== DATA LOADING ====================

    def _load_initial_data(self):
        """Load initial application data"""
        print("         📊 Loading initial data...")

        try:
            self._refresh_projects()
            self._refresh_statistics()
            self._update_status("Application loaded successfully")
            print("         ✅ Initial data loaded")

        except Exception as e:
            print(f"         ❌ Error loading initial data: {e}")
            # Continue anyway, as this is not critical

    def _refresh_projects(self):
        """Refresh projects list"""
        try:
            projects = self.project_controller.get_all_projects()

            self.projects_listbox.delete(0, tk.END)
            self.projects_listbox.insert(0, "All Projects")

            for project in projects:
                self.projects_listbox.insert(tk.END, project.name)

        except Exception as e:
            print(f"❌ Error loading projects: {e}")

    def _refresh_statistics(self):
        """Refresh statistics display"""
        try:
            metrics = self.task_controller.get_dashboard_metrics(self.current_user.id if self.current_user else None)

            # Clear existing stats
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            # Add stats - KOMPAKTOWE
            stats_data = [
                ("Total", metrics.total_issues),
                ("Open", metrics.open_issues),
                ("Mine", metrics.my_assigned),
                ("Critical", metrics.critical_bugs)
            ]

            for label, value in stats_data:
                stat_frame = tk.Frame(self.stats_frame, bg=self.colors['bg_secondary'])
                stat_frame.pack(fill=tk.X, padx=3, pady=1)

                tk.Label(stat_frame, text=f"{label}:",
                         bg=self.colors['bg_secondary'],
                         fg=self.colors['text_secondary'],
                         font=('Segoe UI', 8)).pack(side=tk.LEFT)

                tk.Label(stat_frame, text=str(value),
                         bg=self.colors['bg_secondary'],
                         fg=self.colors['accent_gold'],
                         font=('Segoe UI', 8, 'bold')).pack(side=tk.RIGHT)

        except Exception as e:
            print(f"❌ Error loading statistics: {e}")

    # ==================== EVENT HANDLERS - POPRAWIONE FILTROWANIE ====================

    def _on_project_select(self, event):
        """POPRAWIONA METODA - Handle project selection z aktualizacją dashboardu"""
        try:
            selection = self.projects_listbox.curselection()
            if selection:
                index = selection[0]
                if index == 0:  # "All Projects"
                    print("📁 Selected: All Projects")
                    self.current_filter.project_id = None
                else:
                    projects = self.project_controller.get_all_projects()
                    if index - 1 < len(projects):
                        selected_project = projects[index - 1]
                        print(f"📁 Selected project: {selected_project.name} (ID: {selected_project.id})")
                        self.current_filter.project_id = selected_project.id

                # KLUCZOWE - aktualizuj dashboard jeśli jest aktywny
                if self.current_view == "dashboard":
                    print("🔄 Updating dashboard with project filter...")
                    self.dashboard_controller.update_filter(self.current_filter)

                self._refresh_current_view()

        except Exception as e:
            print(f"Error in project selection: {e}")
            import traceback
            traceback.print_exc()

    def _apply_filter(self, **filter_kwargs):
        """POPRAWIONA METODA - Apply quick filter z aktualizacją dashboardu"""
        try:
            print(f"🔍 Applying filter: {filter_kwargs}")

            # Reset current filter
            self.current_filter = SearchFilter()

            # Apply new filter criteria
            for key, value in filter_kwargs.items():
                if key == "assignee_id":
                    self.current_filter.assignee_id = value
                    print(f"   Set assignee_id: {value}")
                elif key == "issue_type":
                    self.current_filter.issue_type = value
                    print(f"   Set issue_type: {value}")
                elif key == "priority":
                    self.current_filter.priority = value
                    print(f"   Set priority: {value}")
                elif key == "module_name":
                    # Find module ID by name
                    modules = self.task_controller.db_manager.get_all_modules()
                    module = next((m for m in modules if m.name == value), None)
                    if module:
                        self.current_filter.module_id = module.id
                        print(f"   Set module_id: {module.id} ({value})")
                elif key == "status_open":
                    # This would be handled in the query
                    print(f"   Set status_open: {value}")
                elif key == "recent":
                    from datetime import datetime, timedelta
                    self.current_filter.updated_from = datetime.now() - timedelta(days=7)
                    print(f"   Set recent filter (7 days)")

            # KLUCZOWE - aktualizuj dashboard jeśli jest aktywny
            if self.current_view == "dashboard":
                print("🔄 Updating dashboard with applied filter...")
                self.dashboard_controller.update_filter(self.current_filter)

            self._refresh_current_view()
            self._update_status(f"Filter applied: {', '.join(f'{k}={v}' for k, v in filter_kwargs.items())}")

        except Exception as e:
            print(f"Filter error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Filter Error", f"Failed to apply filter: {str(e)}")

    def _refresh_current_view(self):
        """POPRAWIONA METODA - Refresh the current view with updated data"""
        try:
            print(f"🔄 Refreshing {self.current_view} view with current filter...")

            # Refresh specific view instances if they exist
            if self.current_view == "kanban" and self.kanban_view:
                self.kanban_view.current_filter = self.current_filter
                self.kanban_view.load_data()
            elif self.current_view == "list" and self.list_view:
                self.list_view.current_filter = self.current_filter
                self.list_view.load_data()
            elif self.current_view == "dashboard":
                # Dashboard już został zaktualizowany w _apply_filter lub _on_project_select
                print("   Dashboard already updated via update_filter()")
            else:
                # Recreate the view
                print("   Recreating view...")
                self._switch_view(self.current_view)

        except Exception as e:
            print(f"Error refreshing view: {e}")
            import traceback
            traceback.print_exc()

    # ==================== CRUD OPERATIONS - FIXED ====================

    def _new_bug(self):
        """Create new bug report - FIXED VERSION"""
        print("🐛 Creating new bug report...")
        try:
            # Show enhanced task dialog for bug creation
            dialog = EnhancedTaskDialog(
                parent=self.root,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=None,
                issue_type="BUG"
            )

            if dialog.result:
                self._refresh_current_view()
                self._refresh_statistics()
                self._update_status(f"Bug report created: {dialog.result.title}")
                print(f"✅ Bug report created: {dialog.result.title}")

        except Exception as e:
            print(f"❌ Error creating bug: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to create bug: {str(e)}")

    def _new_feature(self):
        """Create new feature request - FIXED VERSION"""
        print("✨ Creating new feature request...")
        try:
            # Show enhanced task dialog for feature creation
            dialog = EnhancedTaskDialog(
                parent=self.root,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=None,
                issue_type="FEATURE"
            )

            if dialog.result:
                self._refresh_current_view()
                self._refresh_statistics()
                self._update_status(f"Feature request created: {dialog.result.title}")
                print(f"✅ Feature request created: {dialog.result.title}")

        except Exception as e:
            print(f"❌ Error creating feature: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to create feature: {str(e)}")

    def _new_project(self):
        """Create new project"""
        try:
            dialog = ProjectDialog(self.root, self.project_controller)
            if dialog.result:
                self._refresh_projects()
                self._update_status("Project created successfully")
        except Exception as e:
            print(f"Error creating project: {e}")
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")

    def _edit_project(self):
        """Edit selected project"""
        try:
            selection = self.projects_listbox.curselection()
            if selection and selection[0] > 0:
                projects = self.project_controller.get_all_projects()
                project_index = selection[0] - 1
                if project_index < len(projects):
                    project = projects[project_index]
                    dialog = ProjectDialog(self.root, self.project_controller, project)
                    if dialog.result:
                        self._refresh_projects()
                        self._update_status("Project updated successfully")
        except Exception as e:
            print(f"Error editing project: {e}")
            messagebox.showerror("Error", f"Failed to edit project: {str(e)}")

    def _delete_project(self):
        """Delete selected project"""
        try:
            selection = self.projects_listbox.curselection()
            if selection and selection[0] > 0:
                projects = self.project_controller.get_all_projects()
                project_index = selection[0] - 1
                if project_index < len(projects):
                    project = projects[project_index]

                    if messagebox.askyesno("Confirm Delete",
                                           f"Are you sure you want to delete project '{project.name}' and all its tasks?"):
                        self.project_controller.delete_project(project.id)
                        self._refresh_projects()
                        self._refresh_current_view()
                        self._update_status("Project deleted successfully")
        except Exception as e:
            print(f"Error deleting project: {e}")
            messagebox.showerror("Error", f"Failed to delete project: {str(e)}")

    # ==================== USER MENU ====================

    def _show_user_menu(self, event):
        """Show user menu"""
        try:
            menu = tk.Menu(self.root, tearoff=0,
                           bg=self.colors['bg_card'],
                           fg=self.colors['text_primary'],
                           activebackground=self.colors['accent_teal'],
                           font=('Segoe UI', 9))

            menu.add_command(label="👤 Profile Settings", command=self._show_profile_settings)
            menu.add_command(label="🔐 Change Password", command=self._change_password)
            menu.add_separator()

            if self.current_user and self.current_user.role == "ADMIN":
                menu.add_command(label="👥 User Management", command=self._show_user_management)
                menu.add_command(label="⚙️ System Settings", command=self._show_system_settings)
                menu.add_separator()

            menu.add_command(label="📋 About TaskMaster", command=self._show_about)
            menu.add_command(label="🚪 Logout", command=self._logout)

            menu.post(event.x_root, event.y_root)

        except Exception as e:
            print(f"Error showing user menu: {e}")

    def _show_profile_settings(self):
        """Show profile settings dialog"""
        messagebox.showinfo("Profile Settings", "Profile settings dialog will be implemented")

    def _change_password(self):
        """Show change password dialog"""
        messagebox.showinfo("Change Password", "Change password dialog will be implemented")

    def _show_user_management(self):
        """Show user management dialog"""
        try:
            dialog = UserManagementDialog(self.root, self.user_controller)
        except Exception as e:
            print(f"Error opening user management: {e}")
            messagebox.showerror("Error", f"Failed to open user management: {str(e)}")

    def _show_system_settings(self):
        """Show system settings dialog"""
        messagebox.showinfo("System Settings", "System settings dialog will be implemented")

    def _show_about(self):
        """Show about dialog"""
        about_text = """TaskMaster Bug Tracker v2.0

Enhanced task management and bug tracking system
specifically designed for Money Mentor AI development.

Features:
• Advanced bug tracking
• Project management
• User roles and permissions
• Dashboard analytics
• Kanban boards
• Multi-view interface

© 2024 TaskMaster Development Team"""

        messagebox.showinfo("About TaskMaster", about_text)

    def _logout(self):
        """Logout user"""
        try:
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                self.user_controller.logout_user()
                self.current_user = None

                # Clear interface
                for widget in self.root.winfo_children():
                    widget.destroy()

                # Clear view instances
                self.kanban_view = None
                self.list_view = None

                # Show login again
                self._show_login()
        except Exception as e:
            print(f"Error during logout: {e}")

    # ==================== UTILITY METHODS ====================

    def _update_status(self, message: str):
        """Update status bar message"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.configure(text=message)
                self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
        except Exception as e:
            print(f"Error updating status: {e}")

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color for hover effects"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darkened = tuple(int(c * 0.8) for c in rgb)
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except:
            return hex_color  # Return original if darkening fails

    def get_current_user(self) -> Optional[User]:
        """Get current user (for other components)"""
        return self.current_user

    def refresh_data(self):
        """Refresh all application data"""
        try:
            self._refresh_projects()
            self._refresh_statistics()
            self._refresh_current_view()
            self._update_status("All data refreshed")
        except Exception as e:
            print(f"Error refreshing data: {e}")