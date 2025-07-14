"""
Enhanced Task Dialog - Create/Edit tasks with bug tracking features
KOMPLETNA WERSJA z funkcjonalnością załączników - POPRAWIONA
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
import os
import shutil
from datetime import datetime
import platform
import mimetypes
import uuid
import subprocess

from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from models.database import DatabaseManager
from models.entities import (
    Task, User, Module, Version, Label, Attachment,
    ISSUE_TYPE_CHOICES, PRIORITY_CHOICES, SEVERITY_CHOICES,
    RESOLUTION_CHOICES, MODULE_CHOICES
)

# Attachment configuration
ATTACHMENT_CONFIG = {
    'max_file_size_mb': 50,          # Maximum file size per attachment
    'max_total_size_mb': 200,        # Maximum total size per task
    'max_files_per_task': 20,        # Maximum number of files per task
    'allowed_extensions': [
        # Images
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg',
        # Documents
        '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages',
        # Spreadsheets
        '.xlsx', '.xls', '.csv', '.ods', '.numbers',
        # Archives
        '.zip', '.rar', '.7z', '.tar', '.gz',
        # Logs
        '.log', '.out', '.txt',
        # Videos (small ones)
        '.mp4', '.avi', '.mov', '.mkv', '.webm',
        # Audio
        '.mp3', '.wav', '.ogg', '.m4a'
    ],
    'blocked_extensions': [
        '.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jar', '.com', '.pif'
    ]
}


class EnhancedTaskDialog:
    """Enhanced dialog for creating and editing tasks/bugs - KOMPLETNA WERSJA z załącznikami"""

    def __init__(self, parent, task_controller: TaskController,
                 project_controller: ProjectController, task: Optional[Task] = None,
                 issue_type: Optional[str] = None):
        self.task_controller = task_controller
        self.project_controller = project_controller
        self.db_manager = DatabaseManager()
        self.task = task
        self.result = None
        self.default_issue_type = issue_type

        # POPRAWIONE KOLORY - Łagodniejsze dla oczu
        self.colors = {
            # Tła podstawowe
            'bg_primary': '#1a222c',
            'bg_secondary': '#2d3748',
            'bg_card': '#374151',
            'bg_hover': '#4b5563',
            'bg_panel': '#1f2937',

            # Teksty
            'text_primary': '#f7fafc',
            'text_secondary': '#cbd5e0',
            'text_muted': '#a0aec0',

            # Akcenty
            'accent_gold': '#E8C547',
            'accent_teal': '#00BFA6',
            'accent_purple': '#9F7AEA',
            'accent_blue': '#3B82F6',
            'critical': '#EF4444',
            'border_light': '#4a5568',

            # Łagodne kolory inputów
            'input_bg': '#475569',
            'input_bg_focus': '#5b6d84',
            'input_fg': '#e2e8f0',
            'input_fg_placeholder': '#94a3b8',
            'input_border': '#64748b',
            'input_border_focus': '#00BFA6',

            # Buttony
            'button_bg': '#374151',
            'button_hover': '#4b5563',

            # Kolory dla różnych stanów
            'dropdown_bg': '#475569',
            'dropdown_hover': '#5b6d84',
            'tab_active': '#E8C547',
            'tab_inactive': '#4a5568',
        }

        # Data lists
        self.users = []
        self.modules = []
        self.versions = []
        self.labels = []
        self.attachments = []

        # Generate task identifier for display
        task_id_str = ""
        if task:
            module_prefix = (task.module_name or "GEN")[:3].upper()
            task_id_str = f" (#{module_prefix}{task.id:03d})"

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        if task:
            dialog_title = f"Edit Issue: {task.title}{task_id_str}"
        else:
            issue_type_name = issue_type or "Issue"
            dialog_title = f"New {issue_type_name}"

        self.dialog.title(dialog_title)
        self.dialog.configure(bg=self.colors['bg_primary'])
        self.dialog.transient(parent)

        # Set window to maximized state
        if platform.system() == 'Windows':
            self.dialog.state('zoomed')
        else:
            self.dialog.attributes('-zoomed', True)

        # Set minimum size
        self.dialog.minsize(1200, 800)
        self.dialog.grab_set()

        # Load data and create interface
        self._load_data()
        self._create_widgets()
        self._load_task_data()

        # Ensure dialog stays on top
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        self.dialog.after(100, lambda: self.dialog.attributes('-topmost', False))

        # Wait for dialog to close
        self.dialog.wait_window()

    def _load_data(self):
        """Load reference data"""
        self.users = self.db_manager.get_all_users()
        self.modules = self.db_manager.get_all_modules()
        self.versions = self.db_manager.get_all_versions()
        self.labels = self.db_manager.get_all_labels()

        if self.task:
            self.attachments = self.db_manager.get_task_attachments(self.task.id)

    def _create_widgets(self):
        """Create dialog widgets with improved visual design"""
        # Main container
        main_container = tk.Frame(self.dialog, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

        # Top section - Header and Buttons
        top_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        top_frame.pack(fill=tk.X, pady=(0, 15))

        # Header with gradient-like effect
        header_frame = tk.Frame(top_frame, bg=self.colors['bg_primary'])
        header_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Icon and title with better spacing
        title_container = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_container.pack(side=tk.LEFT)

        icon = "🐛" if (self.task and self.task.issue_type == "BUG") or self.default_issue_type == "BUG" else "✨"

        # Icon with background
        icon_frame = tk.Frame(title_container, bg=self.colors['accent_teal'], width=50, height=50)
        icon_frame.pack(side=tk.LEFT, padx=(0, 15))
        icon_frame.pack_propagate(False)

        icon_label = tk.Label(icon_frame,
                              text=icon,
                              bg=self.colors['accent_teal'],
                              fg='white',
                              font=('Segoe UI', 20))
        icon_label.pack(expand=True)

        # Title and subtitle
        text_frame = tk.Frame(title_container, bg=self.colors['bg_primary'])
        text_frame.pack(side=tk.LEFT, fill=tk.Y)

        header_label = tk.Label(text_frame,
                                text="Issue Details",
                                bg=self.colors['bg_primary'],
                                fg=self.colors['text_primary'],
                                font=('Segoe UI', 18, 'bold'))
        header_label.pack(anchor='w')

        subtitle_text = "Edit existing issue" if self.task else "Create new issue"
        subtitle_label = tk.Label(text_frame,
                                  text=subtitle_text,
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_secondary'],
                                  font=('Segoe UI', 10))
        subtitle_label.pack(anchor='w')

        # Action buttons with better styling
        button_frame = tk.Frame(top_frame, bg=self.colors['bg_primary'])
        button_frame.pack(side=tk.RIGHT)

        # Save button - main action
        save_text = "💾 Update Issue" if self.task else "✅ Create Issue"
        self.save_btn = self._create_styled_button(button_frame, save_text, self._save_task,
                                                   bg_color=self.colors['accent_gold'],
                                                   fg_color='black', primary=True)
        self.save_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Cancel button - secondary action
        self.cancel_btn = self._create_styled_button(button_frame, "❌ Cancel", self._cancel,
                                                     bg_color=self.colors['button_bg'],
                                                     fg_color=self.colors['text_secondary'])
        self.cancel_btn.pack(side=tk.RIGHT)

        # Content area with improved tabs
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabs with custom styling
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Configure custom styles
        self._configure_enhanced_styles()

        # Create tabs
        self._create_enhanced_details_tab()
        self._create_enhanced_reproduction_tab()
        self._create_enhanced_attachments_tab()
        if self.task:
            self._create_enhanced_activity_tab()

    def _create_styled_button(self, parent, text, command, bg_color, fg_color, primary=False):
        """Create a beautifully styled button"""
        btn = tk.Label(parent,
                       text=text,
                       bg=bg_color,
                       fg=fg_color,
                       font=('Segoe UI', 11, 'bold' if primary else 'normal'),
                       padx=20,
                       pady=12,
                       cursor='hand2',
                       relief='flat')

        # Hover effects
        def on_enter(e):
            btn.configure(bg=self._lighten_color(bg_color, 0.1))

        def on_leave(e):
            btn.configure(bg=bg_color)

        def on_click(e):
            command()

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)

        return btn

    def _configure_enhanced_styles(self):
        """Configure enhanced TTK styles for better visual appeal"""
        style = ttk.Style()

        try:
            style.theme_use('clam')
        except:
            pass

        # Notebook - main container
        style.configure('Enhanced.TNotebook',
                        background=self.colors['bg_secondary'],
                        borderwidth=0,
                        tabmargins=[0, 0, 0, 0])

        # Tab styling
        style.configure('Enhanced.TNotebook.Tab',
                        background=self.colors['tab_inactive'],
                        foreground=self.colors['text_secondary'],
                        padding=[20, 12],
                        borderwidth=0,
                        focuscolor='none',
                        font=('Segoe UI', 10, 'bold'))

        # Tab states mapping
        style.map('Enhanced.TNotebook.Tab',
                  background=[('selected', self.colors['tab_active']),
                              ('active', self.colors['bg_hover']),
                              ('!selected', self.colors['tab_inactive'])],
                  foreground=[('selected', 'black'),
                              ('active', self.colors['text_primary']),
                              ('!selected', self.colors['text_secondary'])],
                  expand=[('selected', [1, 1, 1, 0])])

        # Enhanced Combobox styling
        style.configure('Enhanced.TCombobox',
                        fieldbackground=self.colors['input_bg'],
                        background=self.colors['dropdown_bg'],
                        foreground=self.colors['input_fg'],
                        bordercolor=self.colors['input_border'],
                        lightcolor=self.colors['input_border'],
                        darkcolor=self.colors['input_border'],
                        borderwidth=2,
                        relief='flat',
                        font=('Segoe UI', 10))

        # Combobox states
        style.map('Enhanced.TCombobox',
                  fieldbackground=[('readonly', self.colors['input_bg']),
                                   ('focus', self.colors['input_bg_focus']),
                                   ('disabled', self.colors['bg_card'])],
                  foreground=[('readonly', self.colors['input_fg']),
                              ('disabled', self.colors['text_muted'])],
                  bordercolor=[('focus', self.colors['input_border_focus']),
                               ('!focus', self.colors['input_border'])],
                  selectbackground=[('readonly', self.colors['accent_teal'])],
                  selectforeground=[('readonly', 'white')])

        # Apply enhanced style to notebook
        self.notebook.configure(style='Enhanced.TNotebook')

    def _create_enhanced_details_tab(self):
        """
        Create enhanced main details tab - NAPRAWIONA WERSJA z pełną szerokością jak Reproduction
        """
        details_frame = tk.Frame(self.notebook, bg=self.colors['bg_secondary'])
        self.notebook.add(details_frame, text="📋 Details")

        # === SCROLLABLE CONTENT - PRZYWRÓCONE SCROLLOWANIE ===
        canvas = tk.Canvas(details_frame, bg=self.colors['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_secondary'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # KLUCZOWE: Rozciągnij zawartość do pełnej szerokości canvas
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas.find_all()[0], width=canvas_width)

        scrollable_frame.bind('<Configure>', configure_scroll_region)
        canvas.bind('<Configure>', configure_canvas_width)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === GŁÓWNA KARTA W SCROLLABLE FRAME ===
        content_card = self._create_form_card(scrollable_frame, "📝 Issue Details")
        content_card.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        content_inner = tk.Frame(content_card, bg=self.colors['bg_card'])
        content_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # === TITLE - PEŁNA SZEROKOŚĆ ===
        self._create_enhanced_label(content_inner, "📋 Title *", required=True)
        self.title_var = tk.StringVar()
        self.title_entry = self._create_enhanced_entry_fullwidth(content_inner, self.title_var)

        # === ISSUE PROPERTIES - 3 kolumny obok siebie ===
        self._create_enhanced_label(content_inner, "⚙️ Issue Properties", section=True)

        properties_container = tk.Frame(content_inner, bg=self.colors['bg_card'])
        properties_container.pack(fill=tk.X, pady=(5, 20))

        # Kolumna 1 - Issue Type, Priority
        col1 = tk.Frame(properties_container, bg=self.colors['bg_card'])
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        self._create_enhanced_label(col1, "Issue Type")
        self.issue_type_var = tk.StringVar()
        self.issue_type_combo = self._create_enhanced_combobox_fullwidth(col1, self.issue_type_var,
                                                                         [choice[1] for choice in ISSUE_TYPE_CHOICES])

        self._create_enhanced_label(col1, "Priority")
        self.priority_var = tk.StringVar()
        self.priority_combo = self._create_enhanced_combobox_fullwidth(col1, self.priority_var,
                                                                       [choice[1] for choice in PRIORITY_CHOICES])

        # Kolumna 2 - Severity, Status
        col2 = tk.Frame(properties_container, bg=self.colors['bg_card'])
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 15))

        self._create_enhanced_label(col2, "Severity")
        self.severity_var = tk.StringVar()
        self.severity_combo = self._create_enhanced_combobox_fullwidth(col2, self.severity_var,
                                                                       [choice[1] for choice in SEVERITY_CHOICES])

        self._create_enhanced_label(col2, "Status")
        self.status_var = tk.StringVar()
        statuses = self.task_controller.get_all_statuses()
        status_names = [status.name for status in statuses]
        self.status_combo = self._create_enhanced_combobox_fullwidth(col2, self.status_var, status_names)

        # Kolumna 3 - Project, Module
        col3 = tk.Frame(properties_container, bg=self.colors['bg_card'])
        col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))

        self._create_enhanced_label(col3, "Project")
        self.project_var = tk.StringVar()
        projects = self.project_controller.get_all_projects()
        project_names = [project.name for project in projects]
        self.project_combo = self._create_enhanced_combobox_fullwidth(col3, self.project_var, project_names)

        self._create_enhanced_label(col3, "Module")
        self.module_var = tk.StringVar()
        module_names = [f"{module.display_name}" for module in self.modules]
        self.module_combo = self._create_enhanced_combobox_fullwidth(col3, self.module_var, module_names)

        # === DESCRIPTION - PEŁNA SZEROKOŚĆ ===
        self._create_enhanced_label(content_inner, "📝 Description", section=True)
        self.description_text = self._create_enhanced_text_area_fullwidth(content_inner, height=5)

        # === ASSIGNMENT - 2 kolumny obok siebie ===
        self._create_enhanced_label(content_inner, "👥 Assignment", section=True)

        assignment_container = tk.Frame(content_inner, bg=self.colors['bg_card'])
        assignment_container.pack(fill=tk.X, pady=(5, 20))

        # Reporter
        reporter_col = tk.Frame(assignment_container, bg=self.colors['bg_card'])
        reporter_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        self._create_enhanced_label(reporter_col, "Reporter")
        self.reporter_var = tk.StringVar()
        user_names = [f"{user.full_name} ({user.username})" for user in self.users]
        self.reporter_combo = self._create_enhanced_combobox_fullwidth(reporter_col, self.reporter_var, user_names)

        # Assignee
        assignee_col = tk.Frame(assignment_container, bg=self.colors['bg_card'])
        assignee_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))

        self._create_enhanced_label(assignee_col, "Assignee")
        self.assignee_var = tk.StringVar()
        assignee_names = ["Unassigned"] + user_names
        self.assignee_combo = self._create_enhanced_combobox_fullwidth(assignee_col, self.assignee_var, assignee_names)

        # === TIME ESTIMATES - 2 kolumny obok siebie ===
        self._create_enhanced_label(content_inner, "⏱️ Time Estimates", section=True)

        time_container = tk.Frame(content_inner, bg=self.colors['bg_card'])
        time_container.pack(fill=tk.X, pady=(5, 20))

        # Estimated Hours
        estimated_col = tk.Frame(time_container, bg=self.colors['bg_card'])
        estimated_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        self._create_enhanced_label(estimated_col, "Estimated Hours")
        self.estimated_hours_var = tk.StringVar()
        self.estimated_hours_entry = self._create_enhanced_entry_fullwidth(estimated_col, self.estimated_hours_var)

        # Time Spent
        spent_col = tk.Frame(time_container, bg=self.colors['bg_card'])
        spent_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))

        self._create_enhanced_label(spent_col, "Time Spent")
        self.time_spent_var = tk.StringVar()
        self.time_spent_entry = self._create_enhanced_entry_fullwidth(spent_col, self.time_spent_var)

        # === VERSIONS - 2 kolumny obok siebie ===
        self._create_enhanced_label(content_inner, "🔧 Versions", section=True)

        versions_container = tk.Frame(content_inner, bg=self.colors['bg_card'])
        versions_container.pack(fill=tk.X, pady=(5, 20))

        # Affected Version
        affected_col = tk.Frame(versions_container, bg=self.colors['bg_card'])
        affected_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        self._create_enhanced_label(affected_col, "Affected Version")
        self.affected_version_var = tk.StringVar()
        version_names = ["None"] + [version.name for version in self.versions]
        self.affected_version_combo = self._create_enhanced_combobox_fullwidth(affected_col, self.affected_version_var, version_names)

        # Fix Version
        fix_col = tk.Frame(versions_container, bg=self.colors['bg_card'])
        fix_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))

        self._create_enhanced_label(fix_col, "Fix Version")
        self.fix_version_var = tk.StringVar()
        self.fix_version_combo = self._create_enhanced_combobox_fullwidth(fix_col, self.fix_version_var, version_names)

        # === LABELS - PEŁNA SZEROKOŚĆ ===
        self._create_enhanced_label(content_inner, "🏷️ Labels", section=True)
        self._create_enhanced_labels_widget_fullwidth(content_inner)

        # === RESOLUTION (jeśli istnieje) - 2 kolumny obok siebie ===
        if self.task and self.task.resolution:
            self._create_enhanced_label(content_inner, "✅ Resolution", section=True)

            resolution_container = tk.Frame(content_inner, bg=self.colors['bg_card'])
            resolution_container.pack(fill=tk.X, pady=(5, 20))

            # Resolution Type
            resolution_type_col = tk.Frame(resolution_container, bg=self.colors['bg_card'])
            resolution_type_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

            self._create_enhanced_label(resolution_type_col, "Resolution Type")
            self.resolution_var = tk.StringVar()
            self.resolution_combo = self._create_enhanced_combobox_fullwidth(resolution_type_col, self.resolution_var,
                                                                             [choice[1] for choice in RESOLUTION_CHOICES])

            # Resolution Notes
            resolution_notes_col = tk.Frame(resolution_container, bg=self.colors['bg_card'])
            resolution_notes_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))

            self._create_enhanced_label(resolution_notes_col, "Resolution Notes")
            self.resolution_notes_var = tk.StringVar()
            self.resolution_notes_entry = self._create_enhanced_entry_fullwidth(resolution_notes_col, self.resolution_notes_var)

    def _create_enhanced_reproduction_tab(self):
        """Create enhanced reproduction tab"""
        repro_frame = tk.Frame(self.notebook, bg=self.colors['bg_secondary'])
        self.notebook.add(repro_frame, text="🔬 Reproduction")

        # Main content in a card
        content_card = self._create_form_card(repro_frame, "🔬 Bug Reproduction Details")
        content_card.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        content_inner = tk.Frame(content_card, bg=self.colors['bg_card'])
        content_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # Environment
        self._create_enhanced_label(content_inner, "🖥️ Environment")
        self.environment_var = tk.StringVar()
        self.environment_entry = self._create_enhanced_entry_fullwidth(content_inner, self.environment_var)

        hint_label = tk.Label(content_inner,
                              text="e.g., Windows 11, Java 23, Chrome 120, Exante Broker",
                              bg=self.colors['bg_card'],
                              fg=self.colors['text_muted'],
                              font=('Segoe UI', 9, 'italic'))
        hint_label.pack(anchor='w', pady=(2, 15))

        # Steps to Reproduce
        self._create_enhanced_label(content_inner, "📋 Steps to Reproduce")
        self.steps_text = self._create_enhanced_text_area_fullwidth(content_inner, height=6,
                                                                    placeholder="1. Go to...\n2. Click on...\n3. Enter...")

        # Expected vs Actual - side by side
        results_frame = tk.Frame(content_inner, bg=self.colors['bg_card'])
        results_frame.pack(fill=tk.X, pady=(15, 15))

        # Expected Result
        expected_frame = tk.Frame(results_frame, bg=self.colors['bg_card'])
        expected_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._create_enhanced_label(expected_frame, "✅ Expected Result")
        self.expected_text = self._create_enhanced_text_area_fullwidth(expected_frame, height=4)

        # Actual Result
        actual_frame = tk.Frame(results_frame, bg=self.colors['bg_card'])
        actual_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self._create_enhanced_label(actual_frame, "❌ Actual Result")
        self.actual_text = self._create_enhanced_text_area_fullwidth(actual_frame, height=4)

        # Stack Trace
        self._create_enhanced_label(content_inner, "🐛 Stack Trace / Error Details")
        self.stack_trace_text = self._create_enhanced_text_area_fullwidth(content_inner, height=8)

    def _create_enhanced_attachments_tab(self):
        """Create enhanced attachments tab with FULL FUNCTIONALITY"""
        attachments_frame = tk.Frame(self.notebook, bg=self.colors['bg_secondary'])
        self.notebook.add(attachments_frame, text="📎 Attachments")

        # Main card
        content_card = self._create_form_card(attachments_frame, "📎 File Attachments")
        content_card.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        content_inner = tk.Frame(content_card, bg=self.colors['bg_card'])
        content_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # Header with upload button and info
        header_frame = tk.Frame(content_inner, bg=self.colors['bg_card'])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        upload_info = tk.Label(header_frame,
                               text="Upload screenshots, logs, or other relevant files",
                               bg=self.colors['bg_card'],
                               fg=self.colors['text_secondary'],
                               font=('Segoe UI', 10))
        upload_info.pack(side=tk.LEFT)

        upload_btn = self._create_styled_button(header_frame, "📁 Add File", self._add_attachment,
                                                bg_color=self.colors['accent_teal'], fg_color='white')
        upload_btn.pack(side=tk.RIGHT)

        # File limits info
        limits_info = tk.Label(content_inner,
                               text=f"Max file size: {ATTACHMENT_CONFIG['max_file_size_mb']}MB • "
                                    f"Max total: {ATTACHMENT_CONFIG['max_total_size_mb']}MB • "
                                    f"Max files: {ATTACHMENT_CONFIG['max_files_per_task']}",
                               bg=self.colors['bg_card'],
                               fg=self.colors['text_muted'],
                               font=('Segoe UI', 9))
        limits_info.pack(pady=(0, 15))

        # Attachments list area
        self.attachments_list_frame = tk.Frame(content_inner, bg=self.colors['bg_panel'])
        self.attachments_list_frame.pack(fill=tk.BOTH, expand=True)

        self._refresh_enhanced_attachments_list()

    def _create_enhanced_activity_tab(self):
        """Create enhanced activity tab"""
        activity_frame = tk.Frame(self.notebook, bg=self.colors['bg_secondary'])
        self.notebook.add(activity_frame, text="📜 Activity")

        # Main card
        content_card = self._create_form_card(activity_frame, "💬 Comments & Activity")
        content_card.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        content_inner = tk.Frame(content_card, bg=self.colors['bg_card'])
        content_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # Add comment section
        add_comment_card = self._create_mini_card(content_inner, "✍️ Add Comment")
        add_comment_card.pack(fill=tk.X, pady=(0, 20))

        add_comment_inner = tk.Frame(add_comment_card, bg=self.colors['bg_panel'])
        add_comment_inner.pack(fill=tk.X, padx=15, pady=15)

        self.new_comment_text = self._create_enhanced_text_area_fullwidth(add_comment_inner, height=3)

        add_comment_btn_frame = tk.Frame(add_comment_inner, bg=self.colors['bg_panel'])
        add_comment_btn_frame.pack(fill=tk.X, pady=(10, 0))

        add_btn = self._create_styled_button(add_comment_btn_frame, "💬 Add Comment", self._add_comment,
                                             bg_color=self.colors['accent_purple'], fg_color='white')
        add_btn.pack()

        # Comments list
        self.comments_list_frame = tk.Frame(content_inner, bg=self.colors['bg_card'])
        self.comments_list_frame.pack(fill=tk.BOTH, expand=True)

        self._load_enhanced_comments()

    # === NOWE METODY DLA PEŁNEJ SZEROKOŚCI ===

    def _create_enhanced_label(self, parent, text, required=False, section=False):
        """Create enhanced form label with full width support"""
        label_text = text
        if required:
            label_text += " *"

        color = self.colors['accent_gold'] if required else self.colors['text_primary']
        if section:
            color = self.colors['accent_teal']

        font_size = 11 if section else 10
        font_weight = 'bold'

        label = tk.Label(parent, text=label_text,
                         bg=parent['bg'],
                         fg=color,
                         font=('Segoe UI', font_size, font_weight))

        if section:
            label.pack(anchor='w', pady=(15, 5))
        else:
            label.pack(anchor='w', pady=(8, 3))

        return label

    def _create_enhanced_entry_fullwidth(self, parent, textvariable):
        """Create enhanced entry with FULL WIDTH"""
        entry = tk.Entry(parent, textvariable=textvariable,
                         bg=self.colors['input_bg'],
                         fg=self.colors['input_fg'],
                         insertbackground=self.colors['accent_gold'],
                         font=('Segoe UI', 10),
                         relief='flat',
                         bd=2,
                         highlightthickness=2,
                         highlightcolor=self.colors['input_border_focus'],
                         highlightbackground=self.colors['input_border'])

        # PEŁNA SZEROKOŚĆ
        entry.pack(fill=tk.X, pady=(0, 12))

        # Focus effects
        def on_focus_in(e):
            entry.configure(bg=self.colors['input_bg_focus'])

        def on_focus_out(e):
            entry.configure(bg=self.colors['input_bg'])

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        return entry

    def _create_enhanced_combobox_fullwidth(self, parent, textvariable, values):
        """Create enhanced combobox with FULL WIDTH"""
        combo = ttk.Combobox(parent, textvariable=textvariable, values=values,
                             state="readonly", font=('Segoe UI', 10),
                             style='Enhanced.TCombobox')

        # PEŁNA SZEROKOŚĆ
        combo.pack(fill=tk.X, pady=(0, 12))
        return combo

    def _create_enhanced_text_area_fullwidth(self, parent, height=4, placeholder=""):
        """Create enhanced text area with FULL WIDTH"""
        text = tk.Text(parent, height=height,
                       bg=self.colors['input_bg'],
                       fg=self.colors['input_fg'],
                       insertbackground=self.colors['accent_gold'],
                       font=('Segoe UI', 10), wrap=tk.WORD,
                       relief='flat',
                       bd=2,
                       highlightthickness=2,
                       highlightcolor=self.colors['input_border_focus'],
                       highlightbackground=self.colors['input_border'])

        # PEŁNA SZEROKOŚĆ
        text.pack(fill=tk.X, pady=(5, 15))

        if placeholder:
            text.insert(1.0, placeholder)
            text.configure(fg=self.colors['input_fg_placeholder'])

            def on_focus_in(event):
                if text.get(1.0, tk.END).strip() == placeholder:
                    text.delete(1.0, tk.END)
                    text.configure(fg=self.colors['input_fg'])
                text.configure(bg=self.colors['input_bg_focus'])

            def on_focus_out(event):
                text.configure(bg=self.colors['input_bg'])
                if not text.get(1.0, tk.END).strip():
                    text.insert(1.0, placeholder)
                    text.configure(fg=self.colors['input_fg_placeholder'])

            text.bind("<FocusIn>", on_focus_in)
            text.bind("<FocusOut>", on_focus_out)
        else:
            # Just focus effects for non-placeholder text areas
            def on_focus_in(event):
                text.configure(bg=self.colors['input_bg_focus'])

            def on_focus_out(event):
                text.configure(bg=self.colors['input_bg'])

            text.bind("<FocusIn>", on_focus_in)
            text.bind("<FocusOut>", on_focus_out)

        return text

    def _create_enhanced_labels_widget_fullwidth(self, parent):
        """Create enhanced labels selection widget with FULL WIDTH"""
        labels_container = tk.Frame(parent, bg=self.colors['bg_card'])
        labels_container.pack(fill=tk.X, pady=(5, 15))

        # Info text
        info_label = tk.Label(labels_container,
                              text="Select relevant labels for this issue:",
                              bg=self.colors['bg_card'],
                              fg=self.colors['text_secondary'],
                              font=('Segoe UI', 9))
        info_label.pack(anchor='w', pady=(0, 10))

        # Labels grid with FULL WIDTH
        self.label_vars = {}
        labels_grid = tk.Frame(labels_container, bg=self.colors['bg_card'])
        labels_grid.pack(fill=tk.X)

        # 5 kolumn dla jeszcze lepszego wykorzystania przestrzeni
        cols_per_row = 5
        current_row_frame = None

        for i, label in enumerate(self.labels):
            if i % cols_per_row == 0:
                current_row_frame = tk.Frame(labels_grid, bg=self.colors['bg_card'])
                current_row_frame.pack(fill=tk.X, pady=2)

            var = tk.BooleanVar()
            self.label_vars[label.id] = var

            # Checkbox frame z PEŁNĄ SZEROKOŚCIĄ
            cb_frame = tk.Frame(current_row_frame, bg=self.colors['bg_panel'], relief='flat', bd=1)
            cb_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)

            cb = tk.Checkbutton(cb_frame,
                                text=label.name,
                                variable=var,
                                bg=self.colors['bg_panel'],
                                fg=self.colors['text_primary'],
                                selectcolor=self.colors['input_bg'],
                                activebackground=self.colors['bg_hover'],
                                activeforeground=self.colors['text_primary'],
                                highlightthickness=0,
                                font=('Segoe UI', 9))
            cb.pack(padx=6, pady=3)

    # Enhanced helper methods for creating form elements

    def _create_form_card(self, parent, title):
        """Create a card container for form sections"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1)

        # Card header
        header = tk.Frame(card, bg=self.colors['bg_hover'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_label = tk.Label(header, text=title,
                               bg=self.colors['bg_hover'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 12, 'bold'))
        title_label.pack(side=tk.LEFT, padx=15, pady=10)

        return card

    def _create_mini_card(self, parent, title):
        """Create a smaller card for sub-sections"""
        card = tk.Frame(parent, bg=self.colors['bg_panel'], relief='flat', bd=1)

        # Mini header
        header = tk.Frame(card, bg=self.colors['bg_panel'])
        header.pack(fill=tk.X, padx=10, pady=(8, 0))

        title_label = tk.Label(header, text=title,
                               bg=self.colors['bg_panel'],
                               fg=self.colors['text_secondary'],
                               font=('Segoe UI', 10, 'bold'))
        title_label.pack(side=tk.LEFT)

        return card

    # ==================== KOMPLETNA FUNKCJONALNOŚĆ ZAŁĄCZNIKÓW ====================

    def _add_attachment(self):
        """Add file attachment with full implementation - KOMPLETNA METODA"""
        if not self.task:
            messagebox.showwarning("Warning", "Please save the task first before adding attachments.")
            return

        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff"),
            ("Document files", "*.pdf *.doc *.docx *.txt *.rtf *.odt"),
            ("Spreadsheet files", "*.xlsx *.xls *.csv *.ods"),
            ("Archive files", "*.zip *.rar *.7z *.tar.gz"),
            ("Log files", "*.log *.txt *.out"),
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("All files", "*.*")
        ]

        filenames = filedialog.askopenfilenames(
            title="Select file(s) to attach",
            filetypes=filetypes
        )

        if not filenames:
            return

        try:
            # Sprawdź obecną liczbę załączników
            current_count = len(self.attachments)
            if current_count + len(filenames) > ATTACHMENT_CONFIG['max_files_per_task']:
                messagebox.showerror("Too Many Files",
                                     f"Too many attachments. Maximum {ATTACHMENT_CONFIG['max_files_per_task']} files per task.\n"
                                     f"Current: {current_count}, Trying to add: {len(filenames)}")
                return

            # Sprawdź rozmiar plików
            total_size = 0
            max_file_size = ATTACHMENT_CONFIG['max_file_size_mb'] * 1024 * 1024
            max_total_size = ATTACHMENT_CONFIG['max_total_size_mb'] * 1024 * 1024

            for filename in filenames:
                if not os.path.exists(filename):
                    messagebox.showerror("File Not Found", f"File '{filename}' not found.")
                    return

                file_size = os.path.getsize(filename)
                if file_size > max_file_size:
                    messagebox.showerror("File Too Large",
                                         f"File '{os.path.basename(filename)}' is too large.\n"
                                         f"Maximum file size: {ATTACHMENT_CONFIG['max_file_size_mb']}MB")
                    return
                total_size += file_size

                # Sprawdź rozszerzenie
                ext = os.path.splitext(filename)[1].lower()
                if ext in ATTACHMENT_CONFIG['blocked_extensions']:
                    messagebox.showerror("File Type Blocked",
                                         f"File type '{ext}' is not allowed for security reasons.")
                    return

            # Sprawdź obecny rozmiar załączników
            current_total_size = sum(att.file_size or 0 for att in self.attachments)
            if current_total_size + total_size > max_total_size:
                messagebox.showerror("Total Size Too Large",
                                     f"Total file size would exceed limit.\n"
                                     f"Current: {self._format_file_size(current_total_size)}\n"
                                     f"Adding: {self._format_file_size(total_size)}\n"
                                     f"Maximum: {ATTACHMENT_CONFIG['max_total_size_mb']}MB")
                return

            # Sprawdź czy folder attachments istnieje
            from utils.helpers import get_app_data_dir
            attachments_dir = os.path.join(get_app_data_dir(), 'attachments')
            os.makedirs(attachments_dir, exist_ok=True)

            # Załącz każdy plik
            success_count = 0
            for filename in filenames:
                if self._attach_single_file(filename, attachments_dir):
                    success_count += 1

            # Odśwież listę załączników
            self.attachments = self.db_manager.get_task_attachments(self.task.id)
            self._refresh_enhanced_attachments_list()

            # Pokaż potwierdzenie
            if success_count == len(filenames):
                if len(filenames) == 1:
                    messagebox.showinfo("Success", "File attached successfully!")
                else:
                    messagebox.showinfo("Success", f"{success_count} files attached successfully!")
            elif success_count > 0:
                messagebox.showwarning("Partial Success",
                                       f"{success_count} of {len(filenames)} files attached successfully.")
            else:
                messagebox.showerror("Failed", "No files were attached.")

        except Exception as e:
            print(f"❌ Error adding attachments: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to attach files: {str(e)}")

    def _attach_single_file(self, source_path: str, attachments_dir: str) -> bool:
        """Attach a single file to the task"""
        try:
            # Wygeneruj unikalną nazwę pliku
            original_filename = os.path.basename(source_path)
            file_extension = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"

            # Ścieżka docelowa
            target_path = os.path.join(attachments_dir, unique_filename)

            # Skopiuj plik
            shutil.copy2(source_path, target_path)

            # Pobierz informacje o pliku
            file_size = os.path.getsize(target_path)
            content_type = mimetypes.guess_type(source_path)[0] or 'application/octet-stream'

            # Dodaj do bazy danych (załóżmy że current_user_id = 1)
            current_user_id = 1  # W prawdziwej aplikacji z sesji użytkownika

            attachment_id = self.task_controller.add_attachment(
                task_id=self.task.id,
                filename=unique_filename,
                original_filename=original_filename,
                file_path=target_path,
                file_size=file_size,
                content_type=content_type,
                uploaded_by=current_user_id
            )

            print(f"✅ File attached: {original_filename} -> {unique_filename}")
            return True

        except Exception as e:
            print(f"❌ Error attaching file {source_path}: {e}")
            messagebox.showerror("Error", f"Failed to attach {os.path.basename(source_path)}: {str(e)}")
            return False

    def _refresh_enhanced_attachments_list(self):
        """Refresh attachments list with enhanced styling and functionality"""
        # Clear existing items
        for widget in self.attachments_list_frame.winfo_children():
            widget.destroy()

        if not self.attachments:
            empty_frame = tk.Frame(self.attachments_list_frame, bg=self.colors['bg_panel'])
            empty_frame.pack(fill=tk.BOTH, expand=True)

            empty_label = tk.Label(empty_frame,
                                   text="📁 No attachments yet\n\nClick 'Add File' to upload screenshots, logs, or documents",
                                   bg=self.colors['bg_panel'], fg=self.colors['text_muted'],
                                   font=('Segoe UI', 11),
                                   justify=tk.CENTER)
            empty_label.pack(expand=True)
            return

        # Show attachment stats
        total_size = sum(att.file_size or 0 for att in self.attachments)
        stats_label = tk.Label(self.attachments_list_frame,
                               text=f"📊 {len(self.attachments)} files • {self._format_file_size(total_size)} total",
                               bg=self.colors['bg_panel'], fg=self.colors['text_secondary'],
                               font=('Segoe UI', 9))
        stats_label.pack(pady=(5, 10))

        # Create scrollable frame for many attachments
        if len(self.attachments) > 5:
            canvas = tk.Canvas(self.attachments_list_frame, bg=self.colors['bg_panel'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(self.attachments_list_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_panel'])

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            target_frame = scrollable_frame
        else:
            target_frame = self.attachments_list_frame

        for attachment in self.attachments:
            self._create_enhanced_attachment_item_with_actions(attachment, target_frame)

    def _create_enhanced_attachment_item_with_actions(self, attachment, parent):
        """Create enhanced attachment list item with action buttons"""
        item_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1)
        item_frame.pack(fill=tk.X, padx=5, pady=3)

        # File icon and info (left side)
        info_frame = tk.Frame(item_frame, bg=self.colors['bg_card'])
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=10)

        # File type icon
        icon = self._get_file_icon(attachment.content_type, attachment.original_filename)

        icon_label = tk.Label(info_frame, text=icon,
                              bg=self.colors['bg_card'], fg=self.colors['accent_teal'],
                              font=('Segoe UI', 16))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # File details
        details_frame = tk.Frame(info_frame, bg=self.colors['bg_card'])
        details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Filename (clickable)
        filename_label = tk.Label(details_frame,
                                  text=attachment.original_filename,
                                  bg=self.colors['bg_card'], fg=self.colors['accent_gold'],
                                  font=('Segoe UI', 10, 'bold'),
                                  cursor='hand2')
        filename_label.pack(anchor='w')
        filename_label.bind("<Button-1>", lambda e: self._open_attachment(attachment))

        # Upload info
        upload_info = f"Uploaded by {attachment.uploaded_by_name or 'Unknown'}"
        if attachment.uploaded_at:
            upload_info += f" on {attachment.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
        upload_info += f" • {self._format_file_size(attachment.file_size)}"

        info_label = tk.Label(details_frame, text=upload_info,
                              bg=self.colors['bg_card'], fg=self.colors['text_muted'],
                              font=('Segoe UI', 9))
        info_label.pack(anchor='w')

        # Action buttons (right side)
        actions_frame = tk.Frame(item_frame, bg=self.colors['bg_card'])
        actions_frame.pack(side=tk.RIGHT, padx=15, pady=10)

        # Open button
        open_btn = self._create_styled_button(actions_frame, "📂 Open",
                                              lambda: self._open_attachment(attachment),
                                              bg_color=self.colors['accent_purple'], fg_color='white')
        open_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Download button - POPRAWIONY: zmieniono initialname na initialfile
        download_btn = self._create_styled_button(actions_frame, "💾 Save",
                                                  lambda: self._save_attachment(attachment),
                                                  bg_color=self.colors['accent_teal'], fg_color='white')
        download_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Preview button (for images)
        if self._is_image_file(attachment):
            preview_btn = self._create_styled_button(actions_frame, "👁️",
                                                     lambda: self._show_attachment_preview(attachment),
                                                     bg_color=self.colors['accent_blue'], fg_color='white')
            preview_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Delete button
        delete_btn = self._create_styled_button(actions_frame, "🗑️",
                                                lambda: self._delete_attachment(attachment),
                                                bg_color=self.colors['critical'], fg_color='white')
        delete_btn.pack(side=tk.RIGHT, padx=(5, 0))

    def _get_file_icon(self, content_type: str, filename: str) -> str:
        """Get appropriate icon for file type"""
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
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            return "🖼️"
        elif ext in ['.pdf']:
            return "📄"
        elif ext in ['.txt', '.log']:
            return "📝"
        elif ext in ['.zip', '.rar', '.7z']:
            return "📦"
        elif ext in ['.xlsx', '.xls', '.csv']:
            return "📊"
        elif ext in ['.mp4', '.avi', '.mov']:
            return "🎥"
        else:
            return "📎"

    def _format_file_size(self, size_bytes: int) -> str:
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

    def _is_image_file(self, attachment) -> bool:
        """Check if attachment is an image file"""
        if attachment.content_type:
            return attachment.content_type.startswith('image/')

        ext = os.path.splitext(attachment.original_filename)[1].lower()
        return ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff']

    def _open_attachment(self, attachment):
        """Open attachment with default system application"""
        try:
            if os.path.exists(attachment.file_path):
                if platform.system() == 'Windows':
                    os.startfile(attachment.file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', attachment.file_path])
                else:  # Linux
                    subprocess.call(['xdg-open', attachment.file_path])

                print(f"📂 Opened attachment: {attachment.original_filename}")
            else:
                messagebox.showerror("File Not Found",
                                     f"File '{attachment.original_filename}' was not found.\n"
                                     "It may have been moved or deleted.")
        except Exception as e:
            print(f"❌ Error opening attachment: {e}")
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def _save_attachment(self, attachment):
        """Save attachment to user-selected location - POPRAWIONA WERSJA"""
        try:
            if not os.path.exists(attachment.file_path):
                messagebox.showerror("File Not Found",
                                     f"File '{attachment.original_filename}' was not found.")
                return

            # Ask user where to save - POPRAWIONE: zmieniono initialname na initialfile
            save_path = filedialog.asksaveasfilename(
                title="Save attachment as...",
                initialfile=attachment.original_filename,  # POPRAWKA: było initialname
                defaultextension=os.path.splitext(attachment.original_filename)[1]
            )

            if save_path:
                shutil.copy2(attachment.file_path, save_path)
                messagebox.showinfo("Success", f"File saved to:\n{save_path}")
                print(f"💾 Attachment saved: {attachment.original_filename} -> {save_path}")

        except Exception as e:
            print(f"❌ Error saving attachment: {e}")
            messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def _delete_attachment(self, attachment):
        """Delete attachment after confirmation"""
        try:
            # Confirm deletion
            result = messagebox.askyesno("Confirm Deletion",
                                         f"Are you sure you want to delete '{attachment.original_filename}'?\n\n"
                                         "This action cannot be undone.")

            if not result:
                return

            # Delete from database and file system
            success = self.task_controller.delete_attachment(attachment.id)

            if success:
                # Refresh list
                self.attachments = self.db_manager.get_task_attachments(self.task.id)
                self._refresh_enhanced_attachments_list()

                messagebox.showinfo("Success", "Attachment deleted successfully.")
                print(f"✅ Attachment deleted: {attachment.original_filename}")
            else:
                messagebox.showerror("Error", "Could not delete attachment.")

        except Exception as e:
            print(f"❌ Error deleting attachment: {e}")
            messagebox.showerror("Error", f"Could not delete attachment: {str(e)}")

    def _show_attachment_preview(self, attachment):
        """Show attachment preview in popup window"""
        if not self._is_image_file(attachment):
            messagebox.showinfo("Preview", "Preview is only available for image files.")
            return

        if not os.path.exists(attachment.file_path):
            messagebox.showerror("File Not Found", "Cannot preview: file not found.")
            return

        try:
            # Create preview window
            preview_window = tk.Toplevel(self.dialog)
            preview_window.title(f"Preview: {attachment.original_filename}")
            preview_window.configure(bg=self.colors['bg_primary'])
            preview_window.transient(self.dialog)
            preview_window.grab_set()

            # Center and size window
            preview_window.geometry("800x600")

            # Try to load image with PIL if available
            try:
                from PIL import Image, ImageTk

                # Load and resize image
                with Image.open(attachment.file_path) as img:
                    # Calculate size to fit in window
                    img_width, img_height = img.size
                    max_width, max_height = 750, 550

                    if img_width > max_width or img_height > max_height:
                        ratio = min(max_width/img_width, max_height/img_height)
                        new_width = int(img_width * ratio)
                        new_height = int(img_height * ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(img)

                    # Create label with image
                    label = tk.Label(preview_window, image=photo, bg=self.colors['bg_primary'])
                    label.image = photo  # Keep reference
                    label.pack(expand=True)

                    # Add close button
                    close_btn = self._create_styled_button(preview_window, "Close",
                                                           preview_window.destroy,
                                                           bg_color=self.colors['accent_gold'],
                                                           fg_color='black')
                    close_btn.pack(pady=10)

            except ImportError:
                # PIL not available - show basic info
                info_text = f"Image Preview\n\nFilename: {attachment.original_filename}\n"
                info_text += f"Size: {self._format_file_size(attachment.file_size)}\n"
                info_text += f"Type: {attachment.content_type}\n\n"
                info_text += "Install PIL (pillow) for image preview:\n"
                info_text += "pip install pillow"

                label = tk.Label(preview_window, text=info_text,
                                 bg=self.colors['bg_primary'],
                                 fg=self.colors['text_primary'],
                                 font=('Segoe UI', 12),
                                 justify=tk.CENTER)
                label.pack(expand=True, padx=20, pady=20)

                close_btn = self._create_styled_button(preview_window, "Close",
                                                       preview_window.destroy,
                                                       bg_color=self.colors['accent_gold'],
                                                       fg_color='black')
                close_btn.pack(pady=10)

        except Exception as e:
            print(f"❌ Error showing preview: {e}")
            messagebox.showerror("Preview Error", f"Could not show preview: {str(e)}")

    # ==================== RESZTA METOD BEZ ZMIAN ====================

    def _load_enhanced_comments(self):
        """Load task comments with enhanced styling"""
        if not self.task:
            return

        comments = self.task_controller.get_task_comments(self.task.id)

        if not comments:
            empty_label = tk.Label(self.comments_list_frame,
                                   text="💬 No comments yet\n\nBe the first to add a comment!",
                                   bg=self.colors['bg_card'], fg=self.colors['text_muted'],
                                   font=('Segoe UI', 11),
                                   justify=tk.CENTER)
            empty_label.pack(expand=True, pady=30)
            return

        for comment in comments:
            self._create_enhanced_comment_item(comment)

    def _create_enhanced_comment_item(self, comment):
        """Create enhanced comment item"""
        item_frame = tk.Frame(self.comments_list_frame, bg=self.colors['bg_panel'],
                              relief='flat', bd=1)
        item_frame.pack(fill=tk.X, pady=5)

        # Comment header
        header_frame = tk.Frame(item_frame, bg=self.colors['bg_hover'])
        header_frame.pack(fill=tk.X)

        # Author avatar (first letter of name)
        author_name = comment.author_name or "Unknown User"
        avatar_text = author_name[0].upper() if author_name else "?"

        avatar_label = tk.Label(header_frame, text=avatar_text,
                                bg=self.colors['accent_purple'], fg='white',
                                font=('Segoe UI', 12, 'bold'),
                                width=3, height=1)
        avatar_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Author info
        info_frame = tk.Frame(header_frame, bg=self.colors['bg_hover'])
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        author_label = tk.Label(info_frame, text=author_name,
                                bg=self.colors['bg_hover'], fg=self.colors['text_primary'],
                                font=('Segoe UI', 10, 'bold'))
        author_label.pack(anchor='w')

        date_str = comment.created_at.strftime("%Y-%m-%d %H:%M") if comment.created_at else ""
        date_label = tk.Label(info_frame, text=date_str,
                              bg=self.colors['bg_hover'], fg=self.colors['text_muted'],
                              font=('Segoe UI', 9))
        date_label.pack(anchor='w')

        # Comment content
        content_frame = tk.Frame(item_frame, bg=self.colors['bg_panel'])
        content_frame.pack(fill=tk.X, padx=15, pady=10)

        content_label = tk.Label(content_frame, text=comment.content,
                                 bg=self.colors['bg_panel'], fg=self.colors['text_primary'],
                                 font=('Segoe UI', 10), wraplength=600, justify=tk.LEFT)
        content_label.pack(fill=tk.X)

    # Color utility methods
    def _lighten_color(self, hex_color: str, factor: float = 0.1) -> str:
        """Lighten a hex color by factor"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
            return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
        except:
            return hex_color

    def _darken_color(self, hex_color: str, factor: float = 0.2) -> str:
        """Darken a hex color by factor"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darkened = tuple(int(c * (1 - factor)) for c in rgb)
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except:
            return hex_color

    # Data loading methods (bez zmian z oryginału)
    def _load_task_data(self):
        """Load task data into form"""
        if not self.task:
            # Set defaults for new task
            if self.default_issue_type:
                type_map = {choice[0]: choice[1] for choice in ISSUE_TYPE_CHOICES}
                if self.default_issue_type in type_map:
                    self.issue_type_var.set(type_map[self.default_issue_type])

            # Set default priority to Medium
            self.priority_var.set("🟡 Medium (P2)")
            self.severity_var.set("🟡 Minor")

            # Set default reporter to current user (admin for now)
            if self.users:
                self.reporter_var.set(f"{self.users[0].full_name} ({self.users[0].username})")

            # Set default project and status
            projects = self.project_controller.get_all_projects()
            if projects:
                self.project_var.set(projects[0].name)

            statuses = self.task_controller.get_all_statuses()
            if statuses:
                self.status_var.set(statuses[0].name)

            return

        # Load existing task data (ta sama logika co w oryginale)
        self.title_var.set(self.task.title)

        if self.task.description:
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, self.task.description)

        # Set combobox values
        type_map = {choice[0]: choice[1] for choice in ISSUE_TYPE_CHOICES}
        if self.task.issue_type in type_map:
            self.issue_type_var.set(type_map[self.task.issue_type])

        priority_map = {choice[0]: choice[1] for choice in PRIORITY_CHOICES}
        if self.task.priority in priority_map:
            self.priority_var.set(priority_map[self.task.priority])

        severity_map = {choice[0]: choice[1] for choice in SEVERITY_CHOICES}
        if self.task.severity in severity_map:
            self.severity_var.set(severity_map[self.task.severity])

        if self.task.project_name:
            self.project_var.set(self.task.project_name)

        if self.task.status_name:
            self.status_var.set(self.task.status_name)

        if self.task.module_name:
            self.module_var.set(self.task.module_name)

        # Set user fields
        if self.task.reporter_name:
            reporter_text = next((f"{user.full_name} ({user.username})" for user in self.users
                                  if user.id == self.task.reporter_id), "")
            if reporter_text:
                self.reporter_var.set(reporter_text)

        if self.task.assignee_name:
            assignee_text = next((f"{user.full_name} ({user.username})" for user in self.users
                                  if user.id == self.task.assignee_id), "Unassigned")
            self.assignee_var.set(assignee_text)
        else:
            self.assignee_var.set("Unassigned")

        # Set version fields
        if self.task.affected_version_name:
            self.affected_version_var.set(self.task.affected_version_name)
        else:
            self.affected_version_var.set("None")

        if self.task.fix_version_name:
            self.fix_version_var.set(self.task.fix_version_name)
        else:
            self.fix_version_var.set("None")

        # Set time fields
        if self.task.estimated_hours:
            self.estimated_hours_var.set(str(self.task.estimated_hours))
        if self.task.time_spent:
            self.time_spent_var.set(str(self.task.time_spent))

        # Set reproduction fields
        if hasattr(self, 'environment_var'):
            if self.task.environment:
                self.environment_var.set(self.task.environment)
            if self.task.steps_to_reproduce:
                self.steps_text.delete(1.0, tk.END)
                self.steps_text.insert(1.0, self.task.steps_to_reproduce)
            if self.task.expected_result:
                self.expected_text.delete(1.0, tk.END)
                self.expected_text.insert(1.0, self.task.expected_result)
            if self.task.actual_result:
                self.actual_text.delete(1.0, tk.END)
                self.actual_text.insert(1.0, self.task.actual_result)
            if self.task.stack_trace:
                self.stack_trace_text.delete(1.0, tk.END)
                self.stack_trace_text.insert(1.0, self.task.stack_trace)

        # Set labels
        if self.task.labels:
            for label in self.task.labels:
                if label.id in self.label_vars:
                    self.label_vars[label.id].set(True)

    # Action methods (bez zmian logiki)
    def _save_task(self):
        """Save task with validation"""
        # Validate required fields
        if not self.title_var.get().strip():
            messagebox.showerror("Validation Error", "Title is required")
            return

        if not self.project_var.get():
            messagebox.showerror("Validation Error", "Project is required")
            return

        try:
            # Get reference IDs (ta sama logika co w oryginale)
            projects = self.project_controller.get_all_projects()
            project = next((p for p in projects if p.name == self.project_var.get()), None)
            if not project:
                messagebox.showerror("Error", "Invalid project selected")
                return

            statuses = self.task_controller.get_all_statuses()
            status = next((s for s in statuses if s.name == self.status_var.get()), None)
            if not status:
                messagebox.showerror("Error", "Invalid status selected")
                return

            # Get issue type
            issue_type_value = next((choice[0] for choice in ISSUE_TYPE_CHOICES
                                     if choice[1] == self.issue_type_var.get()), "TASK")

            # Get priority and severity
            priority_value = next((choice[0] for choice in PRIORITY_CHOICES
                                   if choice[1] == self.priority_var.get()), 3)
            severity_value = next((choice[0] for choice in SEVERITY_CHOICES
                                   if choice[1] == self.severity_var.get()), 3)

            # Get user IDs
            reporter_id = self._get_user_id_from_display(self.reporter_var.get())
            assignee_id = self._get_user_id_from_display(self.assignee_var.get()) if self.assignee_var.get() != "Unassigned" else None

            # Get module ID
            module_id = None
            if self.module_var.get():
                module = next((m for m in self.modules if m.display_name == self.module_var.get()), None)
                if module:
                    module_id = module.id

            # Get version IDs
            affected_version_id = None
            if self.affected_version_var.get() != "None":
                version = next((v for v in self.versions if v.name == self.affected_version_var.get()), None)
                if version:
                    affected_version_id = version.id

            fix_version_id = None
            if self.fix_version_var.get() != "None":
                version = next((v for v in self.versions if v.name == self.fix_version_var.get()), None)
                if version:
                    fix_version_id = version.id

            # Get time estimates
            estimated_hours = None
            if self.estimated_hours_var.get():
                try:
                    estimated_hours = float(self.estimated_hours_var.get())
                except ValueError:
                    pass

            time_spent = None
            if self.time_spent_var.get():
                try:
                    time_spent = float(self.time_spent_var.get())
                except ValueError:
                    pass

            # Get reproduction data
            environment = self.environment_var.get() if hasattr(self, 'environment_var') else None
            steps = self.steps_text.get(1.0, tk.END).strip() if hasattr(self, 'steps_text') else None
            expected = self.expected_text.get(1.0, tk.END).strip() if hasattr(self, 'expected_text') else None
            actual = self.actual_text.get(1.0, tk.END).strip() if hasattr(self, 'actual_text') else None
            stack_trace = self.stack_trace_text.get(1.0, tk.END).strip() if hasattr(self, 'stack_trace_text') else None

            # Create task object
            task_data = Task(
                id=self.task.id if self.task else None,
                project_id=project.id,
                title=self.title_var.get().strip(),
                description=self.description_text.get(1.0, tk.END).strip() or None,
                status_id=status.id,
                priority=priority_value,
                issue_type=issue_type_value,
                severity=severity_value,
                reporter_id=reporter_id,
                assignee_id=assignee_id,
                module_id=module_id,
                affected_version_id=affected_version_id,
                fix_version_id=fix_version_id,
                environment=environment,
                steps_to_reproduce=steps,
                expected_result=expected,
                actual_result=actual,
                stack_trace=stack_trace,
                estimated_hours=estimated_hours,
                time_spent=time_spent
            )

            # Save task
            if self.task:
                self.task_controller.update_task(task_data)
                task_id = self.task.id
                print(f"✅ Task updated: {task_data.title}")
            else:
                task_id = self.task_controller.create_task(task_data)
                task_data.id = task_id  # Set the ID for newly created task
                print(f"✅ Task created: {task_data.title}")

            # Handle labels
            if hasattr(self, 'label_vars'):
                # Remove existing labels
                if self.task:
                    for label in self.labels:
                        self.db_manager.remove_label_from_task(task_id, label.id)

                # Add selected labels
                for label_id, var in self.label_vars.items():
                    if var.get():
                        self.db_manager.add_label_to_task(task_id, label_id)

            self.result = task_data
            self.dialog.destroy()

        except Exception as e:
            print(f"❌ Error saving task: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to save task: {str(e)}")

    def _get_user_id_from_display(self, display_text: str) -> Optional[int]:
        """Get user ID from display text"""
        if not display_text:
            return None

        # Extract username from "Full Name (username)" format
        if "(" in display_text and ")" in display_text:
            username = display_text.split("(")[1].split(")")[0]
            user = next((u for u in self.users if u.username == username), None)
            return user.id if user else None

        return None

    def _add_comment(self):
        """Add new comment"""
        if not self.task:
            return

        content = self.new_comment_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Comment cannot be empty")
            return

        try:
            self.task_controller.add_comment(self.task.id, content)
            self.new_comment_text.delete(1.0, tk.END)

            # Refresh comments
            for widget in self.comments_list_frame.winfo_children():
                widget.destroy()
            self._load_enhanced_comments()

            print(f"✅ Comment added to task: {self.task.title}")

        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            messagebox.showerror("Error", f"Failed to add comment: {str(e)}")

    def _cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()