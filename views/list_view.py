"""
Enhanced List View - Tabular task management view for TaskMaster
NAPRAWIONA WERSJA z idealną kolorystyką i zaawansowanym filtrowaniem
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from models.entities import Task, SearchFilter, PRIORITY_CHOICES, ISSUE_TYPE_CHOICES
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from views.enhanced_task_dialog import EnhancedTaskDialog
from utils.helpers import format_date, format_relative_date


class EnhancedListView:
    """Enhanced list view with perfect dark theme colors and advanced filtering"""

    def __init__(self, parent_frame, parent_window, task_controller: TaskController,
                 project_controller: ProjectController):
        self.parent_frame = parent_frame
        self.parent_window = parent_window
        self.task_controller = task_controller
        self.project_controller = project_controller

        # Data
        self.tasks: List[Task] = []
        self.filtered_tasks: List[Task] = []
        self.current_filter = SearchFilter()
        self.sort_column = "updated_at"
        self.sort_reverse = True

        # Multiple selection filters - NOWE!
        self.selected_statuses: Set[str] = set()
        self.selected_priorities: Set[int] = set()
        self.selected_types: Set[str] = set()
        self.selected_projects: Set[int] = set()

        # UI state
        self.selected_task_id: Optional[int] = None

        # IDEALNE KOLORY - w pełni zgodne z ciemnym motywem
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

            # Priorytety - ciemne tło, jasny tekst
            'priority_critical': '#7F1D1D',    # Ciemny czerwony
            'priority_high': '#92400E',        # Ciemny pomarańczowy
            'priority_medium': '#1E3A8A',      # Ciemny niebieski
            'priority_low': '#064E3B',         # Ciemny zielony
            'priority_trivial': '#374151',     # Szary

            # Teksty priorytetów - jasne na ciemnym tle
            'priority_critical_text': '#FEE2E2',
            'priority_high_text': '#FED7AA',
            'priority_medium_text': '#DBEAFE',
            'priority_low_text': '#D1FAE5',
            'priority_trivial_text': '#F3F4F6',

            # Tabela - NOWE kolory
            'table_bg': '#1f2937',           # Ciemne tło tabeli
            'table_header_bg': '#111827',     # Bardzo ciemne tło nagłówków
            'table_header_fg': '#F9FAFB',     # Jasny tekst nagłówków
            'table_row_even': '#1f2937',      # Parzyste wiersze
            'table_row_odd': '#374151',       # Nieparzyste wiersze
            'table_selected': '#1e40af',      # Zaznaczony wiersz
            'table_border': '#4B5563',        # Obwódki

            'border_light': '#4a5568',
        }

        self.create_view()
        self.load_data()

    def create_view(self):
        """Create the enhanced list view layout"""
        # Clear existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        # Main container
        main_container = tk.Frame(self.parent_frame, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header with title and controls
        self._create_header(main_container)

        # NOWY zaawansowany panel filtrów
        self._create_advanced_filter_panel(main_container)

        # List area z poprawionymi kolorami
        self._create_enhanced_list_area(main_container)

        # Bottom toolbar
        self._create_bottom_toolbar(main_container)

    def _create_header(self, parent):
        """Create header with title"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame,
                               text="📄 Enhanced List View",
                               bg=self.colors['bg_primary'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT, pady=15)

        # Task count
        self.task_count_label = tk.Label(header_frame,
                                         text="",
                                         bg=self.colors['bg_primary'],
                                         fg=self.colors['text_secondary'],
                                         font=('Segoe UI', 10))
        self.task_count_label.pack(side=tk.LEFT, padx=(15, 0), pady=15)

        # Filter status indicator - NOWE!
        self.filter_status_label = tk.Label(header_frame,
                                            text="",
                                            bg=self.colors['bg_primary'],
                                            fg=self.colors['accent_gold'],
                                            font=('Segoe UI', 9, 'italic'))
        self.filter_status_label.pack(side=tk.LEFT, padx=(15, 0), pady=15)

        # Action buttons
        actions_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # New task button
        new_task_btn = tk.Label(actions_frame,
                                text="➕ New Task",
                                bg=self.colors['accent_teal'],
                                fg='white',
                                font=('Segoe UI', 9, 'bold'),
                                padx=12, pady=6, cursor='hand2')
        new_task_btn.pack(side=tk.LEFT, padx=5)
        new_task_btn.bind("<Button-1>", lambda e: self._new_task())

        # Export button
        export_btn = tk.Label(actions_frame,
                              text="📥 Export",
                              bg=self.colors['accent_purple'],
                              fg='white',
                              font=('Segoe UI', 9, 'bold'),
                              padx=12, pady=6, cursor='hand2')
        export_btn.pack(side=tk.LEFT, padx=5)
        export_btn.bind("<Button-1>", lambda e: self._export_tasks())

        # Refresh button
        refresh_btn = tk.Label(actions_frame,
                               text="🔄 Refresh",
                               bg=self.colors['bg_secondary'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 9, 'bold'),
                               padx=12, pady=6, cursor='hand2')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        refresh_btn.bind("<Button-1>", lambda e: self.load_data())

        # Add hover effects
        for btn in [new_task_btn, export_btn, refresh_btn]:
            self._add_button_hover(btn)

    def _create_advanced_filter_panel(self, parent):
        """Create advanced filter panel with multiple selection"""
        filter_main_frame = tk.Frame(parent, bg=self.colors['bg_panel'])
        filter_main_frame.pack(fill=tk.X, padx=20, pady=(10, 0))

        # Filter header
        filter_header = tk.Frame(filter_main_frame, bg=self.colors['bg_panel'])
        filter_header.pack(fill=tk.X, padx=15, pady=(10, 5))

        tk.Label(filter_header,
                 text="🔍 Advanced Filters",
                 bg=self.colors['bg_panel'],
                 fg=self.colors['text_primary'],
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)

        # Toggle button for collapsible filters
        self.filter_expanded = tk.BooleanVar(value=True)
        toggle_btn = tk.Label(filter_header,
                              text="▼ Hide Filters",
                              bg=self.colors['bg_panel'],
                              fg=self.colors['text_secondary'],
                              font=('Segoe UI', 9),
                              cursor='hand2')
        toggle_btn.pack(side=tk.RIGHT)
        toggle_btn.bind("<Button-1>", lambda e: self._toggle_filter_panel())

        # Filter content frame
        self.filter_content_frame = tk.Frame(filter_main_frame, bg=self.colors['bg_panel'])
        self.filter_content_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Row 1: Search and basic filters
        row1 = tk.Frame(self.filter_content_frame, bg=self.colors['bg_panel'])
        row1.pack(fill=tk.X, pady=(0, 10))

        # Search box
        search_frame = tk.Frame(row1, bg=self.colors['bg_panel'])
        search_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(search_frame, text="🔍 Search:",
                 bg=self.colors['bg_panel'],
                 fg=self.colors['text_secondary'],
                 font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_primary'],
                                insertbackground=self.colors['accent_gold'],
                                font=('Segoe UI', 10),
                                width=25, relief='flat', bd=5)
        search_entry.pack(side=tk.LEFT)

        # Clear all filters button
        clear_btn = tk.Label(row1,
                             text="✖ Clear All Filters",
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 9, 'bold'),
                             padx=12, pady=6, cursor='hand2')
        clear_btn.pack(side=tk.RIGHT)
        clear_btn.bind("<Button-1>", lambda e: self._clear_all_filters())
        self._add_button_hover(clear_btn)

        # Row 2: All filters in one row for more space
        row2 = tk.Frame(self.filter_content_frame, bg=self.colors['bg_panel'])
        row2.pack(fill=tk.X, pady=(0, 5))

        # Status filters - NOWE wielokrotne
        self._create_multiple_filter_section(row2, "Status", self._get_statuses(),
                                             self.selected_statuses, self._on_status_filter_change)

        # Priority filters - NOWE wielokrotne
        self._create_multiple_filter_section(row2, "Priority", self._get_priorities(),
                                             self.selected_priorities, self._on_priority_filter_change)

        # Type filters - moved to same row
        self._create_multiple_filter_section(row2, "Type", self._get_issue_types(),
                                             self.selected_types, self._on_type_filter_change)

        # Project filters - moved to same row
        self._create_multiple_filter_section(row2, "Project", self._get_projects(),
                                             self.selected_projects, self._on_project_filter_change)

    def _create_multiple_filter_section(self, parent, label, values, selected_set, callback):
        """Create a multiple selection filter section"""
        section_frame = tk.LabelFrame(parent,
                                      text=f"📋 {label}",
                                      bg=self.colors['bg_panel'],
                                      fg=self.colors['text_primary'],
                                      font=('Segoe UI', 9, 'bold'))
        section_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        # Scrollable frame for many options
        canvas = tk.Canvas(section_frame,
                           bg=self.colors['bg_panel'],
                           height=80, width=150,
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(section_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_panel'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add checkboxes for each value
        self.filter_vars = getattr(self, 'filter_vars', {})
        self.filter_vars[label] = {}

        for value in values:
            if value == "All":
                continue

            var = tk.BooleanVar()
            self.filter_vars[label][value] = var

            checkbox = tk.Checkbutton(scrollable_frame,
                                      text=value,
                                      variable=var,
                                      bg=self.colors['bg_panel'],
                                      fg=self.colors['text_primary'],
                                      selectcolor=self.colors['bg_card'],
                                      activebackground=self.colors['bg_hover'],
                                      activeforeground=self.colors['text_primary'],
                                      font=('Segoe UI', 8),
                                      command=lambda v=value: callback(v))
            checkbox.pack(anchor='w', padx=5, pady=1)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

    def _create_enhanced_list_area(self, parent):
        """Create the main list/table area with perfect dark theme"""
        list_container = tk.Frame(parent, bg=self.colors['bg_primary'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # NOWE - idealne style dla ciemnego motywu
        self._setup_perfect_dark_theme()

        # Treeview frame z ciemnym tłem
        tree_frame = tk.Frame(list_container, bg=self.colors['table_bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        tree_frame.configure(bg=self.colors['table_bg'])  # Podwójna konfiguracja dla pewności

        # Create Treeview
        columns = ('ID', 'Type', 'Title', 'Priority', 'Status', 'Module',
                   'Assignee', 'Reporter', 'Created', 'Updated')

        self.tree = ttk.Treeview(tree_frame,
                                 columns=columns,
                                 show='tree headings',
                                 selectmode='browse',
                                 style='PerfectDark.Treeview')

        # TTK używa stylów, nie bezpośredniej konfiguracji background

        # Configure columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('ID', width=60, anchor='center')
        self.tree.column('Type', width=80, anchor='center')
        self.tree.column('Title', width=350, anchor='w')
        self.tree.column('Priority', width=90, anchor='center')
        self.tree.column('Status', width=120, anchor='center')
        self.tree.column('Module', width=150, anchor='w')
        self.tree.column('Assignee', width=120, anchor='w')
        self.tree.column('Reporter', width=120, anchor='w')
        self.tree.column('Created', width=100, anchor='center')
        self.tree.column('Updated', width=100, anchor='center')

        # Configure headings with sort indicators
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by_column(c))

        # Scrollbars with dark theme
        style = ttk.Style()
        style.configure("Dark.Vertical.TScrollbar",
                        background=self.colors['bg_secondary'],
                        troughcolor=self.colors['bg_primary'],
                        bordercolor=self.colors['border_light'],
                        arrowcolor=self.colors['text_primary'])

        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                    command=self.tree.yview, style="Dark.Vertical.TScrollbar")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal",
                                    command=self.tree.xview, style="Dark.Horizontal.TScrollbar")

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack everything z ciemnym tłem
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Konfiguracja dla lepszego układu
        tree_frame.grid_propagate(False)

        # Bind events
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)
        self.tree.bind('<Return>', lambda e: self._edit_selected_task())
        self.tree.bind('<Delete>', lambda e: self._delete_selected_task())

        # WAŻNE - wymuszenie stylów po stworzeniu - NAPRAWIONE!
        self._force_style_refresh()

    def _setup_perfect_dark_theme(self):
        """Setup perfect dark theme for Treeview - KOMPLETNIE NAPRAWIONE KOLORY"""
        style = ttk.Style()

        # Ustaw motyw jako bazę
        try:
            style.theme_use('clam')
        except:
            pass

        # GŁÓWNY styl Treeview - WSZYSTKIE właściwości dla ciemnego motywu
        style.configure('PerfectDark.Treeview',
                        background=self.colors['table_bg'],           # Główne tło
                        foreground=self.colors['text_primary'],       # Tekst
                        fieldbackground=self.colors['table_bg'],      # Tło pól - KLUCZOWE!
                        insertbackground=self.colors['accent_gold'],  # Kursor
                        selectbackground=self.colors['table_selected'], # Zaznaczenie
                        selectforeground='white',                     # Tekst zaznaczenia
                        borderwidth=0,                               # Bez obwódek
                        highlightthickness=0,                        # Bez podświetlenia
                        relief='flat',                               # Płaski relief
                        font=('Segoe UI', 9),
                        rowheight=25)

        # NAGŁÓWKI - bardzo wyraziste
        style.configure('PerfectDark.Treeview.Heading',
                        background=self.colors['table_header_bg'],
                        foreground=self.colors['table_header_fg'],
                        borderwidth=2,
                        relief='raised',
                        font=('Segoe UI', 10, 'bold'),
                        padding=(8, 6))

        # KLUCZOWE - mapowania stanów z fieldbackground
        style.map('PerfectDark.Treeview',
                  background=[('selected', self.colors['table_selected']),
                              ('active', self.colors['bg_hover']),
                              ('focus', self.colors['table_bg']),
                              ('!focus', self.colors['table_bg']),
                              ('disabled', self.colors['table_bg']),
                              ('readonly', self.colors['table_bg'])],
                  foreground=[('selected', 'white'),
                              ('active', self.colors['text_primary']),
                              ('focus', self.colors['text_primary']),
                              ('!focus', self.colors['text_primary']),
                              ('disabled', self.colors['text_secondary'])],
                  fieldbackground=[('selected', self.colors['table_selected']),
                                   ('active', self.colors['table_bg']),
                                   ('focus', self.colors['table_bg']),
                                   ('!focus', self.colors['table_bg']),
                                   ('disabled', self.colors['table_bg']),
                                   ('readonly', self.colors['table_bg'])])

        # Mapowania nagłówków
        style.map('PerfectDark.Treeview.Heading',
                  background=[('active', self.colors['accent_gold']),
                              ('pressed', self.colors['accent_teal'])],
                  foreground=[('active', 'black'),
                              ('pressed', 'white')],
                  relief=[('pressed', 'sunken')])

        # Style dla scrollbarów - POPRAWIONE
        style.configure("Dark.Horizontal.TScrollbar",
                        background=self.colors['bg_secondary'],
                        troughcolor=self.colors['bg_primary'],
                        bordercolor=self.colors['border_light'],
                        arrowcolor=self.colors['text_primary'],
                        darkcolor=self.colors['bg_secondary'],
                        lightcolor=self.colors['bg_secondary'])

        style.configure("Dark.Vertical.TScrollbar",
                        background=self.colors['bg_secondary'],
                        troughcolor=self.colors['bg_primary'],
                        bordercolor=self.colors['border_light'],
                        arrowcolor=self.colors['text_primary'],
                        darkcolor=self.colors['bg_secondary'],
                        lightcolor=self.colors['bg_secondary'])

        # AGRESYWNE usunięcie białego tła - nadpisz wszystkie domyślne style
        for state in ['active', 'disabled', 'focus', '!focus', 'invalid',
                      'pressed', 'readonly', 'selected', '!selected']:
            try:
                style.map('PerfectDark.Treeview',
                          fieldbackground=[(state, self.colors['table_bg'])])
            except:
                pass

        # Wymuszenie odświeżenia stylu
        try:
            style.theme_settings(style.theme_use(), {
                'PerfectDark.Treeview': {
                    'configure': {
                        'fieldbackground': self.colors['table_bg'],
                        'background': self.colors['table_bg']
                    }
                }
            })
        except:
            pass

    def _force_style_refresh(self):
        """NAPRAWIONA METODA - Wymusza odświeżenie stylów TTK"""
        try:
            # Aktualizuj widget żeby zaaplikować style
            self.tree.update_idletasks()

            # Force style refresh przez rekonfigurację
            if hasattr(self.tree, 'configure'):
                self.tree.configure(style='PerfectDark.Treeview')

            # Dodatkowa aktualizacja stylu
            style = ttk.Style()
            style.configure('PerfectDark.Treeview',
                            fieldbackground=self.colors['table_bg'],
                            background=self.colors['table_bg'])

            print("✅ Style refresh completed")

        except Exception as e:
            print(f"⚠️ Style refresh warning: {e}")
            # Kontynuuj bez błędu - to nie jest krytyczne

    def _create_bottom_toolbar(self, parent):
        """Create bottom toolbar with selection info"""
        toolbar = tk.Frame(parent, bg=self.colors['bg_secondary'])
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        inner_frame = tk.Frame(toolbar, bg=self.colors['bg_secondary'])
        inner_frame.pack(fill=tk.X, padx=15, pady=8)

        # Selection info
        self.selection_label = tk.Label(inner_frame,
                                        text="No tasks selected",
                                        bg=self.colors['bg_secondary'],
                                        fg=self.colors['text_secondary'],
                                        font=('Segoe UI', 9))
        self.selection_label.pack(side=tk.LEFT)

        # Quick actions
        actions_frame = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        actions_frame.pack(side=tk.LEFT, padx=20)

        # Bulk actions
        bulk_delete_btn = tk.Label(actions_frame,
                                   text="🗑️ Delete Selected",
                                   bg=self.colors['priority_critical'],
                                   fg='white',
                                   font=('Segoe UI', 9),
                                   padx=10, pady=4, cursor='hand2')
        bulk_delete_btn.pack(side=tk.LEFT, padx=5)
        bulk_delete_btn.bind("<Button-1>", lambda e: self._bulk_delete())

        # Results info
        self.results_label = tk.Label(inner_frame,
                                      text="",
                                      bg=self.colors['bg_secondary'],
                                      fg=self.colors['text_secondary'],
                                      font=('Segoe UI', 9))
        self.results_label.pack(side=tk.RIGHT)

    def load_data(self):
        """Load and display tasks"""
        print("📄 Loading enhanced list view data...")

        try:
            # Get all tasks
            self.tasks = self.task_controller.search_tasks_advanced(SearchFilter())

            # Apply filters
            self._apply_all_filters()

            # Update display
            self._refresh_tree()

            # Update counts and status
            self._update_counts()
            self._update_filter_status()

            print(f"✅ Loaded {len(self.tasks)} tasks, showing {len(self.filtered_tasks)} after filters")

        except Exception as e:
            print(f"❌ Error loading data: {e}")
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def _apply_all_filters(self):
        """Apply all active filters with multiple selection support"""
        self.filtered_tasks = self.tasks.copy()

        # Search filter
        search_query = self.search_var.get().lower()
        if search_query:
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if (search_query in task.title.lower() or
                    (task.description and search_query in task.description.lower()) or
                    search_query in str(task.id))
            ]

        # Status filter - MULTIPLE SELECTION
        if self.selected_statuses:
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.status_name in self.selected_statuses
            ]

        # Priority filter - MULTIPLE SELECTION
        if self.selected_priorities:
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.priority in self.selected_priorities
            ]

        # Type filter - MULTIPLE SELECTION
        if self.selected_types:
            type_values = set()
            for selected_type in self.selected_types:
                for value, display in ISSUE_TYPE_CHOICES:
                    if display == selected_type:
                        type_values.add(value)
                        break

            if type_values:
                self.filtered_tasks = [
                    task for task in self.filtered_tasks
                    if task.issue_type in type_values
                ]

        # Project filter - MULTIPLE SELECTION
        if self.selected_projects:
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.project_id in self.selected_projects
            ]

    def _refresh_tree(self):
        """Refresh treeview with perfect dark theme colors"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort tasks
        sorted_tasks = self._sort_tasks(self.filtered_tasks)

        # Add tasks to tree with perfect priority colors
        for i, task in enumerate(sorted_tasks):
            # Priority-based styling
            priority_colors = {
                1: ('critical', self.colors['priority_critical'], self.colors['priority_critical_text']),
                2: ('high', self.colors['priority_high'], self.colors['priority_high_text']),
                3: ('medium', self.colors['priority_medium'], self.colors['priority_medium_text']),
                4: ('low', self.colors['priority_low'], self.colors['priority_low_text']),
                5: ('trivial', self.colors['priority_trivial'], self.colors['priority_trivial_text'])
            }

            priority_name, bg_color, fg_color = priority_colors.get(task.priority,
                                                                    ('medium', self.colors['priority_medium'], self.colors['priority_medium_text']))

            # Alternating row colors
            if i % 2 == 0:
                row_tag = f'{priority_name}_even'
                row_bg = bg_color
            else:
                row_tag = f'{priority_name}_odd'
                row_bg = self._darken_color(bg_color, 0.15)

            # Format data
            created_date = format_date(task.created_at) if task.created_at else ''
            updated_date = format_date(task.updated_at) if task.updated_at else ''
            type_display = task.get_issue_type_display()
            priority_display = task.get_priority_display()

            # Insert item
            self.tree.insert('', 'end',
                             values=(
                                 f"#{task.id}",
                                 type_display,
                                 task.title,
                                 priority_display,
                                 task.status_name or '',
                                 task.module_name or '',
                                 task.assignee_name or 'Unassigned',
                                 task.reporter_name or '',
                                 created_date,
                                 updated_date
                             ),
                             tags=(row_tag,))

        # Configure tag colors
        self._configure_perfect_tag_colors()

    def _configure_perfect_tag_colors(self):
        """Configure perfect tag colors for priority-based rows"""
        priorities = {
            1: ('critical', self.colors['priority_critical'], self.colors['priority_critical_text']),
            2: ('high', self.colors['priority_high'], self.colors['priority_high_text']),
            3: ('medium', self.colors['priority_medium'], self.colors['priority_medium_text']),
            4: ('low', self.colors['priority_low'], self.colors['priority_low_text']),
            5: ('trivial', self.colors['priority_trivial'], self.colors['priority_trivial_text'])
        }

        for priority, (name, bg_color, fg_color) in priorities.items():
            # Even rows
            self.tree.tag_configure(
                f'{name}_even',
                background=bg_color,
                foreground=fg_color,
                font=('Segoe UI', 9)
            )

            # Odd rows (slightly darker)
            darker_bg = self._darken_color(bg_color, 0.15)
            self.tree.tag_configure(
                f'{name}_odd',
                background=darker_bg,
                foreground=fg_color,
                font=('Segoe UI', 9)
            )

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by current sort column"""
        if not self.sort_column:
            return tasks

        sort_keys = {
            'ID': lambda t: t.id or 0,
            'Type': lambda t: t.issue_type or '',
            'Title': lambda t: t.title.lower(),
            'Priority': lambda t: t.priority,
            'Status': lambda t: t.status_name or '',
            'Module': lambda t: t.module_name or '',
            'Assignee': lambda t: t.assignee_name or '',
            'Reporter': lambda t: t.reporter_name or '',
            'Created': lambda t: t.created_at or datetime.min,
            'Updated': lambda t: t.updated_at or datetime.min
        }

        key_func = sort_keys.get(self.sort_column, lambda t: t.id)

        try:
            return sorted(tasks, key=key_func, reverse=self.sort_reverse)
        except Exception as e:
            print(f"Sort error: {e}")
            return tasks

    def _update_counts(self):
        """Update task count displays"""
        total = len(self.tasks)
        filtered = len(self.filtered_tasks)

        if total == filtered:
            count_text = f"({total} tasks)"
        else:
            count_text = f"({filtered} of {total} tasks)"

        self.task_count_label.configure(text=count_text)
        self.results_label.configure(text=f"Showing {filtered} results")

    def _update_filter_status(self):
        """Update filter status indicator"""
        active_filters = []

        if self.search_var.get():
            active_filters.append("Search")
        if self.selected_statuses:
            active_filters.append(f"Status({len(self.selected_statuses)})")
        if self.selected_priorities:
            active_filters.append(f"Priority({len(self.selected_priorities)})")
        if self.selected_types:
            active_filters.append(f"Type({len(self.selected_types)})")
        if self.selected_projects:
            active_filters.append(f"Project({len(self.selected_projects)})")

        if active_filters:
            status_text = f"🔍 Filters: {', '.join(active_filters)}"
        else:
            status_text = ""

        self.filter_status_label.configure(text=status_text)

    # ============== NOWE METODY FILTROWANIA ==============

    def _on_search_change(self, *args):
        """Handle search text change"""
        self._apply_all_filters()
        self._refresh_tree()
        self._update_counts()
        self._update_filter_status()

    def _on_status_filter_change(self, status_name):
        """Handle status filter change - multiple selection"""
        if status_name in self.selected_statuses:
            self.selected_statuses.remove(status_name)
        else:
            self.selected_statuses.add(status_name)

        self._apply_all_filters()
        self._refresh_tree()
        self._update_counts()
        self._update_filter_status()

    def _on_priority_filter_change(self, priority_display):
        """Handle priority filter change - multiple selection"""
        # Convert display to value
        priority_value = None
        for value, display in PRIORITY_CHOICES:
            if display == priority_display:
                priority_value = value
                break

        if priority_value:
            if priority_value in self.selected_priorities:
                self.selected_priorities.remove(priority_value)
            else:
                self.selected_priorities.add(priority_value)

        self._apply_all_filters()
        self._refresh_tree()
        self._update_counts()
        self._update_filter_status()

    def _on_type_filter_change(self, type_display):
        """Handle type filter change - multiple selection"""
        if type_display in self.selected_types:
            self.selected_types.remove(type_display)
        else:
            self.selected_types.add(type_display)

        self._apply_all_filters()
        self._refresh_tree()
        self._update_counts()
        self._update_filter_status()

    def _on_project_filter_change(self, project_name):
        """Handle project filter change - multiple selection"""
        # Find project ID by name
        projects = self.project_controller.get_all_projects()
        project_id = None
        for p in projects:
            if p.name == project_name:
                project_id = p.id
                break

        if project_id:
            if project_id in self.selected_projects:
                self.selected_projects.remove(project_id)
            else:
                self.selected_projects.add(project_id)

        self._apply_all_filters()
        self._refresh_tree()
        self._update_counts()
        self._update_filter_status()

    def _clear_all_filters(self):
        """Clear all filters"""
        # Clear search
        self.search_var.set("")

        # Clear all selections
        self.selected_statuses.clear()
        self.selected_priorities.clear()
        self.selected_types.clear()
        self.selected_projects.clear()

        # Clear checkboxes
        if hasattr(self, 'filter_vars'):
            for category, vars_dict in self.filter_vars.items():
                for var in vars_dict.values():
                    var.set(False)

        self._apply_all_filters()
        self._refresh_tree()
        self._update_counts()
        self._update_filter_status()

    def _toggle_filter_panel(self):
        """Toggle filter panel visibility"""
        if self.filter_expanded.get():
            self.filter_content_frame.pack_forget()
            self.filter_expanded.set(False)
        else:
            self.filter_content_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
            self.filter_expanded.set(True)

    def _sort_by_column(self, column):
        """Sort by clicked column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # Update heading to show sort direction
        for col in self.tree['columns']:
            if col == column:
                symbol = ' ▼' if self.sort_reverse else ' ▲'
                self.tree.heading(col, text=col + symbol)
            else:
                self.tree.heading(col, text=col)

        self._refresh_tree()

    # ============== EVENT HANDLERS ==============

    def _on_double_click(self, event):
        """Handle double click on task"""
        selection = self.tree.selection()
        if selection:
            self._edit_selected_task()

    def _on_right_click(self, event):
        """Handle right click - show context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)

            menu = tk.Menu(self.tree, tearoff=0,
                           bg=self.colors['bg_card'],
                           fg=self.colors['text_primary'],
                           activebackground=self.colors['accent_teal'],
                           font=('Segoe UI', 9))

            menu.add_command(label="✏️ Edit Task", command=self._edit_selected_task)
            menu.add_command(label="👁️ View Details", command=self._view_selected_task)
            menu.add_separator()
            menu.add_command(label="📋 Duplicate", command=self._duplicate_selected_task)
            menu.add_separator()
            menu.add_command(label="🗑️ Delete", command=self._delete_selected_task)

            menu.post(event.x_root, event.y_root)

    def _get_selected_task(self) -> Optional[Task]:
        """Get currently selected task"""
        selection = self.tree.selection()
        if not selection:
            return None

        item = self.tree.item(selection[0])
        task_id_str = item['values'][0]
        task_id = int(task_id_str[1:])

        return next((task for task in self.filtered_tasks if task.id == task_id), None)

    # ============== CRUD OPERATIONS ==============

    def _edit_selected_task(self):
        """Edit the selected task"""
        task = self._get_selected_task()
        if not task:
            return

        try:
            dialog = EnhancedTaskDialog(
                parent=self.parent_window.root,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=task
            )

            if dialog.result:
                self.load_data()

        except Exception as e:
            print(f"❌ Error editing task: {e}")
            messagebox.showerror("Error", f"Failed to edit task: {str(e)}")

    def _view_selected_task(self):
        """View task details"""
        self._edit_selected_task()

    def _duplicate_selected_task(self):
        """Duplicate the selected task"""
        task = self._get_selected_task()
        if not task:
            return

        new_task = Task(
            id=None,
            project_id=task.project_id,
            title=f"Copy of {task.title}",
            description=task.description,
            status_id=1,
            priority=task.priority,
            issue_type=task.issue_type,
            severity=task.severity,
            reporter_id=self.parent_window.current_user.id if self.parent_window.current_user else None,
            module_id=task.module_id,
            environment=task.environment,
            steps_to_reproduce=task.steps_to_reproduce,
            expected_result=task.expected_result,
            actual_result=task.actual_result,
            estimated_hours=task.estimated_hours
        )

        try:
            task_id = self.task_controller.create_task(new_task)
            self.load_data()
            self.parent_window._update_status(f"Task duplicated: {new_task.title}")
        except Exception as e:
            print(f"❌ Error duplicating task: {e}")
            messagebox.showerror("Error", f"Failed to duplicate task: {str(e)}")

    def _delete_selected_task(self):
        """Delete the selected task"""
        task = self._get_selected_task()
        if not task:
            return

        response = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this task?\n\n"
            f"Task: {task.title}\n"
            f"ID: #{task.id}\n\n"
            "This action cannot be undone."
        )

        if response:
            try:
                self.task_controller.delete_task(task.id)
                self.load_data()
                self.parent_window._update_status(f"Task deleted: {task.title}")
            except Exception as e:
                print(f"❌ Error deleting task: {e}")
                messagebox.showerror("Error", f"Failed to delete task: {str(e)}")

    def _bulk_delete(self):
        """Delete selected tasks"""
        self._delete_selected_task()

    def _new_task(self):
        """Create new task"""
        try:
            dialog = EnhancedTaskDialog(
                parent=self.parent_window.root,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=None
            )

            if dialog.result:
                self.load_data()
        except Exception as e:
            print(f"❌ Error creating task: {e}")
            messagebox.showerror("Error", f"Failed to create task: {str(e)}")

    def _export_tasks(self):
        """Export filtered tasks to CSV"""
        if not self.filtered_tasks:
            messagebox.showwarning("No Data", "No tasks to export.")
            return

        try:
            from tkinter import filedialog
            from utils.helpers import export_tasks_to_csv

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            if filename:
                export_tasks_to_csv(self.filtered_tasks, filename)
                messagebox.showinfo("Export Complete",
                                    f"Successfully exported {len(self.filtered_tasks)} tasks to:\n{filename}")
        except Exception as e:
            print(f"❌ Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export tasks: {str(e)}")

    # ============== HELPER METHODS ==============

    def _get_projects(self) -> List[str]:
        """Get list of projects for filter"""
        try:
            projects = self.project_controller.get_all_projects()
            return [p.name for p in projects]
        except Exception as e:
            print(f"❌ Error getting projects: {e}")
            return []

    def _get_issue_types(self) -> List[str]:
        """Get list of issue types for filter"""
        return [display for _, display in ISSUE_TYPE_CHOICES]

    def _get_priorities(self) -> List[str]:
        """Get list of priorities for filter"""
        return [display for _, display in PRIORITY_CHOICES]

    def _get_statuses(self) -> List[str]:
        """Get list of statuses for filter"""
        try:
            statuses = self.task_controller.get_all_statuses()
            return [s.name for s in statuses]
        except Exception as e:
            print(f"❌ Error getting statuses: {e}")
            return []

    def _add_button_hover(self, button):
        """Add hover effect to button"""
        original_bg = button['bg']
        hover_bg = self._darken_color(original_bg) if original_bg != self.colors['bg_secondary'] else self.colors['bg_hover']

        def on_enter(e): button.configure(bg=hover_bg)
        def on_leave(e): button.configure(bg=original_bg)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def _darken_color(self, hex_color: str, factor: float = 0.2) -> str:
        """Darken a hex color by factor"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darkened = tuple(int(c * (1 - factor)) for c in rgb)
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except:
            return hex_color


# Kompatybilność z oryginalnym kodem
ListView = EnhancedListView