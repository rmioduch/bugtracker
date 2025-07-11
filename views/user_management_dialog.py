"""
User Management Dialog - Admin interface for managing users
Professional user management with roles, permissions, and activity tracking
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
from datetime import datetime

from controllers.user_controller import UserController
from models.entities import User, UserRole


class UserManagementDialog:
    """Professional user management dialog for administrators"""

    def __init__(self, parent, user_controller: UserController):
        self.user_controller = user_controller
        self.users: List[User] = []
        self.selected_user: Optional[User] = None

        # Soft Dark color palette
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
            'success': '#48BB78',
            'border_light': '#4a5568',
        }

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("User Management - TaskMaster Admin")
        self.dialog.geometry("1000x700")
        self.dialog.configure(bg=self.colors['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._load_users()

        # Wait for dialog to close
        self.dialog.wait_window()

    def _create_widgets(self):
        """Create user management interface"""
        # Main container
        main_frame = tk.Frame(self.dialog, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self._create_header(main_frame)

        # Main content (users list + details)
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create paned window for users list and details
        self.paned_window = tk.PanedWindow(content_frame,
                                           orient=tk.HORIZONTAL,
                                           bg=self.colors['bg_primary'],
                                           sashwidth=3)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left panel - Users list
        self._create_users_list_panel()

        # Right panel - User details
        self._create_user_details_panel()

        # Bottom buttons
        self._create_buttons(main_frame)

    def _create_header(self, parent):
        """Create dialog header"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title with icon
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT)

        icon_label = tk.Label(title_frame,
                              text="👥",
                              bg=self.colors['bg_primary'],
                              fg=self.colors['accent_gold'],
                              font=('Segoe UI', 24))
        icon_label.pack(side=tk.LEFT)

        title_label = tk.Label(title_frame,
                               text="User Management",
                               bg=self.colors['bg_primary'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=(10, 0))

        subtitle_label = tk.Label(title_frame,
                                  text="Manage user accounts, roles, and permissions",
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_secondary'],
                                  font=('Segoe UI', 10))
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

        # Action buttons
        actions_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        actions_frame.pack(side=tk.RIGHT)

        self._create_action_button(actions_frame, "➕ New User", self._new_user)
        self._create_action_button(actions_frame, "🔄 Refresh", self._refresh_users)

    def _create_action_button(self, parent, text, command):
        """Create header action button"""
        btn = tk.Label(parent,
                       text=text,
                       bg=self.colors['accent_teal'],
                       fg='white',
                       font=('Segoe UI', 9, 'bold'),
                       padx=12, pady=6,
                       cursor='hand2')
        btn.pack(side=tk.RIGHT, padx=5)

        def on_click(event):
            command()

        def on_enter(event):
            btn.configure(bg=self._darken_color(self.colors['accent_teal']))

        def on_leave(event):
            btn.configure(bg=self.colors['accent_teal'])

        btn.bind("<Button-1>", on_click)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _create_users_list_panel(self):
        """Create users list panel"""
        # Left panel frame
        users_panel = tk.Frame(self.paned_window,
                               bg=self.colors['bg_secondary'],
                               width=400)
        users_panel.pack_propagate(False)

        # Panel header
        list_header = tk.Label(users_panel,
                               text="👤 Users List",
                               bg=self.colors['bg_secondary'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 12, 'bold'))
        list_header.pack(fill=tk.X, padx=15, pady=(15, 10))

        # Search/filter
        search_frame = tk.Frame(users_panel, bg=self.colors['bg_secondary'])
        search_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        tk.Label(search_frame,
                 text="Search:",
                 bg=self.colors['bg_secondary'],
                 fg=self.colors['text_secondary'],
                 font=('Segoe UI', 9)).pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_primary'],
                                insertbackground=self.colors['accent_gold'],
                                font=('Segoe UI', 9),
                                relief='flat',
                                bd=5)
        search_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Users listbox
        listbox_frame = tk.Frame(users_panel, bg=self.colors['bg_secondary'])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Create custom listbox with user cards
        self.users_frame = tk.Frame(listbox_frame, bg=self.colors['bg_card'])
        self.users_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for users list
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)

        # Canvas for scrolling
        self.users_canvas = tk.Canvas(self.users_frame,
                                      bg=self.colors['bg_card'],
                                      highlightthickness=0,
                                      yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.users_canvas.yview)

        self.scrollable_users_frame = tk.Frame(self.users_canvas, bg=self.colors['bg_card'])
        self.users_canvas.create_window((0, 0), window=self.scrollable_users_frame, anchor="nw")

        self.users_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure scrolling
        def configure_scroll_region(event):
            self.users_canvas.configure(scrollregion=self.users_canvas.bbox("all"))

        self.scrollable_users_frame.bind("<Configure>", configure_scroll_region)

        self.paned_window.add(users_panel)

    def _create_user_details_panel(self):
        """Create user details panel"""
        # Right panel frame
        details_panel = tk.Frame(self.paned_window, bg=self.colors['bg_secondary'])

        # Panel header
        details_header = tk.Label(details_panel,
                                  text="📝 User Details",
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_primary'],
                                  font=('Segoe UI', 12, 'bold'))
        details_header.pack(fill=tk.X, padx=15, pady=(15, 10))

        # Details content
        self.details_frame = tk.Frame(details_panel, bg=self.colors['bg_secondary'])
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Show initial empty state
        self._show_no_user_selected()

        self.paned_window.add(details_panel)

    def _create_buttons(self, parent):
        """Create dialog buttons"""
        button_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        button_frame.pack(fill=tk.X)

        # Close button
        close_btn = tk.Label(button_frame,
                             text="Close",
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 11),
                             padx=20, pady=10,
                             cursor='hand2')
        close_btn.pack(side=tk.RIGHT)

        def on_close_enter(e): close_btn.configure(bg=self.colors['bg_hover'])
        def on_close_leave(e): close_btn.configure(bg=self.colors['bg_secondary'])

        close_btn.bind("<Enter>", on_close_enter)
        close_btn.bind("<Leave>", on_close_leave)
        close_btn.bind("<Button-1>", lambda e: self.dialog.destroy())

    def _load_users(self):
        """Load users from database"""
        try:
            self.users = self.user_controller.get_all_users(active_only=False)
            self._refresh_users_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")

    def _refresh_users_display(self):
        """Refresh users display"""
        # Clear existing user cards
        for widget in self.scrollable_users_frame.winfo_children():
            widget.destroy()

        # Filter users based on search
        search_query = self.search_var.get().lower()
        filtered_users = []

        for user in self.users:
            if (search_query in user.username.lower() or
                    search_query in user.full_name.lower() or
                    search_query in user.email.lower()):
                filtered_users.append(user)

        # Create user cards
        for user in filtered_users:
            self._create_user_card(user)

        # Update scroll region
        self.scrollable_users_frame.update_idletasks()
        self.users_canvas.configure(scrollregion=self.users_canvas.bbox("all"))

    def _create_user_card(self, user: User):
        """Create user card widget"""
        card_frame = tk.Frame(self.scrollable_users_frame,
                              bg=self.colors['bg_primary'],
                              relief='flat',
                              bd=1,
                              cursor='hand2')
        card_frame.pack(fill=tk.X, padx=5, pady=3)

        # User info frame
        info_frame = tk.Frame(card_frame, bg=self.colors['bg_primary'])
        info_frame.pack(fill=tk.X, padx=10, pady=8)

        # User name and role
        name_frame = tk.Frame(info_frame, bg=self.colors['bg_primary'])
        name_frame.pack(fill=tk.X)

        # Role icon
        role_icons = {
            'ADMIN': '👑',
            'DEVELOPER': '💻',
            'TESTER': '🧪',
            'REPORTER': '📝',
            'VIEWER': '👁️'
        }
        role_icon = role_icons.get(user.role, '👤')

        icon_label = tk.Label(name_frame,
                              text=role_icon,
                              bg=self.colors['bg_primary'],
                              fg=self.colors['accent_gold'],
                              font=('Segoe UI', 12))
        icon_label.pack(side=tk.LEFT)

        # Name and username
        name_label = tk.Label(name_frame,
                              text=user.full_name,
                              bg=self.colors['bg_primary'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 10, 'bold'))
        name_label.pack(side=tk.LEFT, padx=(8, 0))

        username_label = tk.Label(name_frame,
                                  text=f"@{user.username}",
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_muted'],
                                  font=('Segoe UI', 9))
        username_label.pack(side=tk.LEFT, padx=(5, 0))

        # Status indicator
        status_color = self.colors['success'] if user.is_active else self.colors['critical']
        status_text = "Active" if user.is_active else "Inactive"

        status_label = tk.Label(name_frame,
                                text=f"● {status_text}",
                                bg=self.colors['bg_primary'],
                                fg=status_color,
                                font=('Segoe UI', 8))
        status_label.pack(side=tk.RIGHT)

        # Role and email
        details_text = f"{user.role} • {user.email}"
        details_label = tk.Label(info_frame,
                                 text=details_text,
                                 bg=self.colors['bg_primary'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 9))
        details_label.pack(fill=tk.X, pady=(3, 0))

        # Click handler
        def on_card_click(event, selected_user=user):
            self._select_user(selected_user)

        # Hover effects
        def on_enter(event):
            card_frame.configure(bg=self.colors['bg_hover'])
            info_frame.configure(bg=self.colors['bg_hover'])
            name_frame.configure(bg=self.colors['bg_hover'])
            for widget in [icon_label, name_label, username_label, status_label, details_label]:
                widget.configure(bg=self.colors['bg_hover'])

        def on_leave(event):
            bg_color = self.colors['accent_purple'] if user == self.selected_user else self.colors['bg_primary']
            card_frame.configure(bg=bg_color)
            info_frame.configure(bg=bg_color)
            name_frame.configure(bg=bg_color)
            for widget in [icon_label, name_label, username_label, status_label, details_label]:
                widget.configure(bg=bg_color)

        # Bind events
        for widget in [card_frame, info_frame, name_frame, icon_label, name_label, username_label, status_label, details_label]:
            widget.bind("<Button-1>", on_card_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        # Highlight selected user
        if user == self.selected_user:
            card_frame.configure(bg=self.colors['accent_purple'])
            info_frame.configure(bg=self.colors['accent_purple'])
            name_frame.configure(bg=self.colors['accent_purple'])
            for widget in [icon_label, name_label, username_label, status_label, details_label]:
                widget.configure(bg=self.colors['accent_purple'])

    def _select_user(self, user: User):
        """Select user and show details"""
        self.selected_user = user
        self._refresh_users_display()
        self._show_user_details(user)

    def _show_user_details(self, user: User):
        """Show detailed user information"""
        # Clear details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # User profile section
        profile_frame = tk.LabelFrame(self.details_frame,
                                      text="👤 Profile Information",
                                      bg=self.colors['bg_secondary'],
                                      fg=self.colors['text_primary'],
                                      font=('Segoe UI', 10, 'bold'),
                                      bd=0)
        profile_frame.pack(fill=tk.X, pady=(0, 15))

        # Profile details
        profile_info = [
            ("Full Name:", user.full_name),
            ("Username:", user.username),
            ("Email:", user.email),
            ("Role:", user.role),
            ("Status:", "Active" if user.is_active else "Inactive"),
            ("Created:", user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "Unknown"),
            ("Last Login:", user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never")
        ]

        for i, (label, value) in enumerate(profile_info):
            detail_frame = tk.Frame(profile_frame, bg=self.colors['bg_secondary'])
            detail_frame.pack(fill=tk.X, padx=10, pady=2)

            tk.Label(detail_frame,
                     text=label,
                     bg=self.colors['bg_secondary'],
                     fg=self.colors['text_secondary'],
                     font=('Segoe UI', 9),
                     width=12,
                     anchor='w').pack(side=tk.LEFT)

            tk.Label(detail_frame,
                     text=str(value),
                     bg=self.colors['bg_secondary'],
                     fg=self.colors['text_primary'],
                     font=('Segoe UI', 9),
                     anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Actions section
        actions_frame = tk.LabelFrame(self.details_frame,
                                      text="⚙️ Actions",
                                      bg=self.colors['bg_secondary'],
                                      fg=self.colors['text_primary'],
                                      font=('Segoe UI', 10, 'bold'),
                                      bd=0)
        actions_frame.pack(fill=tk.X, pady=(0, 15))

        # Action buttons
        actions_container = tk.Frame(actions_frame, bg=self.colors['bg_secondary'])
        actions_container.pack(fill=tk.X, padx=10, pady=10)

        self._create_detail_button(actions_container, "✏️ Edit User",
                                   lambda: self._edit_user(user), 'left')

        self._create_detail_button(actions_container, "🔐 Reset Password",
                                   lambda: self._reset_password(user), 'left')

        if user.is_active:
            self._create_detail_button(actions_container, "🚫 Deactivate",
                                       lambda: self._deactivate_user(user), 'left',
                                       bg_color=self.colors['critical'])
        else:
            self._create_detail_button(actions_container, "✅ Activate",
                                       lambda: self._activate_user(user), 'left',
                                       bg_color=self.colors['success'])

        # Statistics section
        stats_frame = tk.LabelFrame(self.details_frame,
                                    text="📊 Statistics",
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_primary'],
                                    font=('Segoe UI', 10, 'bold'),
                                    bd=0)
        stats_frame.pack(fill=tk.X)

        # Get user statistics
        stats = self.user_controller.get_user_statistics(user.id)

        stats_info = [
            ("Tasks Assigned:", stats["tasks_assigned"]),
            ("Tasks Reported:", stats["tasks_reported"]),
            ("Tasks Completed:", stats["tasks_completed"]),
            ("Comments Added:", stats["comments_added"]),
            ("Avg Resolution (days):", f"{stats['average_resolution_days']:.1f}")
        ]

        for label, value in stats_info:
            stat_frame = tk.Frame(stats_frame, bg=self.colors['bg_secondary'])
            stat_frame.pack(fill=tk.X, padx=10, pady=2)

            tk.Label(stat_frame,
                     text=label,
                     bg=self.colors['bg_secondary'],
                     fg=self.colors['text_secondary'],
                     font=('Segoe UI', 9),
                     width=20,
                     anchor='w').pack(side=tk.LEFT)

            tk.Label(stat_frame,
                     text=str(value),
                     bg=self.colors['bg_secondary'],
                     fg=self.colors['accent_gold'],
                     font=('Segoe UI', 9, 'bold'),
                     anchor='w').pack(side=tk.LEFT)

    def _create_detail_button(self, parent, text, command, side='left', bg_color=None):
        """Create detail panel button"""
        if bg_color is None:
            bg_color = self.colors['accent_teal']

        btn = tk.Label(parent,
                       text=text,
                       bg=bg_color,
                       fg='white',
                       font=('Segoe UI', 9),
                       padx=10, pady=5,
                       cursor='hand2')
        btn.pack(side=side, padx=3)

        def on_click(event):
            command()

        def on_enter(event):
            btn.configure(bg=self._darken_color(bg_color))

        def on_leave(event):
            btn.configure(bg=bg_color)

        btn.bind("<Button-1>", on_click)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _show_no_user_selected(self):
        """Show no user selected state"""
        # Clear details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # No selection message
        no_selection_label = tk.Label(self.details_frame,
                                      text="👤 Select a user to view details",
                                      bg=self.colors['bg_secondary'],
                                      fg=self.colors['text_muted'],
                                      font=('Segoe UI', 12))
        no_selection_label.pack(expand=True)

    # Event handlers
    def _on_search_change(self, *args):
        """Handle search query change"""
        self._refresh_users_display()

    def _refresh_users(self):
        """Refresh users list"""
        self._load_users()

    def _new_user(self):
        """Create new user"""
        dialog = UserEditDialog(self.dialog, self.user_controller)
        if dialog.result:
            self._load_users()

    def _edit_user(self, user: User):
        """Edit user"""
        dialog = UserEditDialog(self.dialog, self.user_controller, user)
        if dialog.result:
            self._load_users()
            self._show_user_details(dialog.result)

    def _reset_password(self, user: User):
        """Reset user password"""
        # Simple password reset dialog
        new_password = tk.simpledialog.askstring(
            "Reset Password",
            f"Enter new password for {user.username}:",
            show='*'
        )

        if new_password:
            try:
                current_user = self.user_controller.get_current_user()
                if current_user:
                    self.user_controller.reset_password(user.id, new_password, current_user.id)
                    messagebox.showinfo("Success", f"Password reset for {user.username}")
                else:
                    messagebox.showerror("Error", "No admin user found")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset password: {str(e)}")

    def _deactivate_user(self, user: User):
        """Deactivate user"""
        if messagebox.askyesno("Confirm", f"Deactivate user {user.username}?"):
            try:
                self.user_controller.deactivate_user(user.id)
                self._load_users()
                user.is_active = False
                self._show_user_details(user)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to deactivate user: {str(e)}")

    def _activate_user(self, user: User):
        """Activate user"""
        try:
            self.user_controller.reactivate_user(user.id)
            self._load_users()
            user.is_active = True
            self._show_user_details(user)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to activate user: {str(e)}")

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color for hover effects"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


class UserEditDialog:
    """Dialog for creating/editing users"""

    def __init__(self, parent, user_controller: UserController, user: Optional[User] = None):
        self.user_controller = user_controller
        self.user = user
        self.result = None

        # Colors
        self.colors = {
            'bg_primary': '#1a222c',
            'bg_secondary': '#2d3748',
            'bg_card': '#374151',
            'text_primary': '#f7fafc',
            'text_secondary': '#cbd5e0',
            'accent_gold': '#E8C547',
            'accent_teal': '#00BFA6',
        }

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        title = f"Edit User: {user.username}" if user else "New User"
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.dialog.configure(bg=self.colors['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        if user:
            self._load_user_data()

        self.dialog.wait_window()

    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = tk.Frame(self.dialog, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_label = tk.Label(main_frame,
                                text="👤 User Details" if self.user else "➕ New User",
                                bg=self.colors['bg_primary'],
                                fg=self.colors['text_primary'],
                                font=('Segoe UI', 14, 'bold'))
        header_label.pack(pady=(0, 20))

        # Form fields
        # Username
        tk.Label(main_frame, text="Username:", bg=self.colors['bg_primary'],
                 fg=self.colors['text_primary'], font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        self.username_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.username_var, bg=self.colors['bg_card'],
                 fg=self.colors['text_primary'], font=('Segoe UI', 10)).pack(fill=tk.X, pady=(5, 10))

        # Full Name
        tk.Label(main_frame, text="Full Name:", bg=self.colors['bg_primary'],
                 fg=self.colors['text_primary'], font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        self.full_name_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.full_name_var, bg=self.colors['bg_card'],
                 fg=self.colors['text_primary'], font=('Segoe UI', 10)).pack(fill=tk.X, pady=(5, 10))

        # Email
        tk.Label(main_frame, text="Email:", bg=self.colors['bg_primary'],
                 fg=self.colors['text_primary'], font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        self.email_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.email_var, bg=self.colors['bg_card'],
                 fg=self.colors['text_primary'], font=('Segoe UI', 10)).pack(fill=tk.X, pady=(5, 10))

        # Role
        tk.Label(main_frame, text="Role:", bg=self.colors['bg_primary'],
                 fg=self.colors['text_primary'], font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(main_frame, textvariable=self.role_var,
                                  values=[role.value for role in UserRole],
                                  state="readonly", font=('Segoe UI', 10))
        role_combo.pack(fill=tk.X, pady=(5, 10))

        # Password (only for new users)
        if not self.user:
            tk.Label(main_frame, text="Password:", bg=self.colors['bg_primary'],
                     fg=self.colors['text_primary'], font=('Segoe UI', 10, 'bold')).pack(anchor='w')
            self.password_var = tk.StringVar()
            tk.Entry(main_frame, textvariable=self.password_var, show="*",
                     bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                     font=('Segoe UI', 10)).pack(fill=tk.X, pady=(5, 10))

        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        button_frame.pack(fill=tk.X, pady=(20, 0))

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        save_btn = tk.Button(button_frame, text="Save", command=self._save_user)
        save_btn.pack(side=tk.RIGHT)

    def _load_user_data(self):
        """Load user data into form"""
        if self.user:
            self.username_var.set(self.user.username)
            self.full_name_var.set(self.user.full_name)
            self.email_var.set(self.user.email)
            self.role_var.set(self.user.role)

    def _save_user(self):
        """Save user"""
        try:
            if self.user:
                # Update existing user
                self.user.username = self.username_var.get()
                self.user.full_name = self.full_name_var.get()
                self.user.email = self.email_var.get()
                self.user.role = self.role_var.get()
                self.user_controller.update_user(self.user)
                self.result = self.user
            else:
                # Create new user
                user_id = self.user_controller.create_user(
                    username=self.username_var.get(),
                    email=self.email_var.get(),
                    full_name=self.full_name_var.get(),
                    password=self.password_var.get(),
                    role=self.role_var.get()
                )
                self.result = self.user_controller.get_user_by_id(user_id)

            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {str(e)}")


# Import for simplified dialog
import tkinter.simpledialog