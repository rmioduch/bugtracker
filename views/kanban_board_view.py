"""
Kanban Board View - Drag & Drop task management board for TaskMaster
Full implementation with column-based task organization
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Tuple
import platform

from models.entities import Task, TaskStatus, SearchFilter
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from views.enhanced_task_dialog import EnhancedTaskDialog


class KanbanBoardView:
    """Kanban board view with drag & drop functionality"""

    def __init__(self, parent_frame, parent_window, task_controller: TaskController,
                 project_controller: ProjectController):
        self.parent_frame = parent_frame
        self.parent_window = parent_window
        self.task_controller = task_controller
        self.project_controller = project_controller

        # UI state
        self.columns: Dict[int, KanbanColumn] = {}
        self.current_filter = SearchFilter()
        self.dragged_task: Optional[DraggableTaskCard] = None
        self.drag_start_pos: Optional[Tuple[int, int]] = None
        self.drag_placeholder: Optional[tk.Frame] = None

        # Colors (Money Mentor AI theme)
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
            'high': '#F59E0B',
            'medium': '#10B981',
            'low': '#6B7280',
            'border_light': '#4a5568',
        }

        # Priority colors
        self.priority_colors = {
            1: self.colors['critical'],    # Critical
            2: self.colors['high'],        # High
            3: self.colors['accent_gold'], # Medium
            4: self.colors['medium'],      # Low
            5: self.colors['low']          # Trivial
        }

        self.create_view()
        self.load_data()

    def create_view(self):
        """Create the kanban board layout"""
        # Clear existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        # Main container
        main_container = tk.Frame(self.parent_frame, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header with title and controls
        self._create_header(main_container)

        # Scrollable kanban board area
        self._create_board_area(main_container)

    def _create_header(self, parent):
        """Create header with title and controls"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Left side - Title
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)

        title_label = tk.Label(title_frame,
                               text="📋 Kanban Board",
                               bg=self.colors['bg_primary'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT, pady=15)

        # Subtitle with task count
        self.task_count_label = tk.Label(title_frame,
                                         text="",
                                         bg=self.colors['bg_primary'],
                                         fg=self.colors['text_secondary'],
                                         font=('Segoe UI', 10))
        self.task_count_label.pack(side=tk.LEFT, padx=(15, 0), pady=15)

        # Right side - Controls
        controls_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Project filter
        project_frame = tk.Frame(controls_frame, bg=self.colors['bg_primary'])
        project_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(project_frame, text="Project:",
                 bg=self.colors['bg_primary'],
                 fg=self.colors['text_secondary'],
                 font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))

        self.project_var = tk.StringVar(value="All Projects")
        self.project_combo = ttk.Combobox(project_frame,
                                          textvariable=self.project_var,
                                          state="readonly",
                                          width=20,
                                          font=('Segoe UI', 9))
        self.project_combo.pack(side=tk.LEFT)
        self.project_combo.bind("<<ComboboxSelected>>", self._on_project_change)

        # Refresh button
        refresh_btn = tk.Label(controls_frame,
                               text="🔄 Refresh",
                               bg=self.colors['accent_purple'],
                               fg='white',
                               font=('Segoe UI', 9, 'bold'),
                               padx=12,
                               pady=6,
                               cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        refresh_btn.bind("<Button-1>", lambda e: self.load_data())

        # Hover effect
        def on_enter(e): refresh_btn.configure(bg=self._darken_color(self.colors['accent_purple']))
        def on_leave(e): refresh_btn.configure(bg=self.colors['accent_purple'])
        refresh_btn.bind("<Enter>", on_enter)
        refresh_btn.bind("<Leave>", on_leave)

    def _create_board_area(self, parent):
        """Create scrollable kanban board area"""
        # Create canvas for horizontal scrolling
        canvas_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Canvas
        self.canvas = tk.Canvas(canvas_frame,
                                bg=self.colors['bg_primary'],
                                highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL,
                                    command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(xscrollcommand=h_scrollbar.set)

        # Board frame inside canvas
        self.board_frame = tk.Frame(self.canvas, bg=self.colors['bg_primary'])
        self.canvas_window = self.canvas.create_window((0, 0),
                                                       window=self.board_frame,
                                                       anchor='nw')

        # Configure canvas scrolling
        self.board_frame.bind('<Configure>', self._on_board_configure)

        # Mouse wheel scrolling
        self.canvas.bind_all("<Control-MouseWheel>", self._on_mousewheel_horizontal)

    def _on_board_configure(self, event):
        """Update canvas scroll region"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Make canvas fill the height
        canvas_height = self.canvas.winfo_height()
        if canvas_height > 1:
            self.canvas.itemconfig(self.canvas_window, height=canvas_height)

    def _on_mousewheel_horizontal(self, event):
        """Handle horizontal mouse wheel scrolling"""
        if platform.system() == 'Windows':
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.canvas.xview_scroll(int(-1 * event.delta), "units")

    def load_data(self):
        """Load tasks and create kanban columns"""
        print("📋 Loading kanban board data...")

        # Clear existing columns
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.columns.clear()

        # Get all statuses
        statuses = self.task_controller.get_all_statuses()

        # Get all tasks based on current filter
        tasks = self.task_controller.search_tasks_advanced(self.current_filter)

        # Update task count
        self.task_count_label.configure(text=f"({len(tasks)} tasks)")

        # Update project combo
        self._update_project_combo()

        # Group tasks by status
        tasks_by_status = {}
        for status in statuses:
            tasks_by_status[status.id] = []

        for task in tasks:
            if task.status_id in tasks_by_status:
                tasks_by_status[task.status_id].append(task)

        # Create columns for each status
        for i, status in enumerate(statuses):
            column = KanbanColumn(
                self.board_frame,
                status,
                tasks_by_status[status.id],
                self.colors,
                self.priority_colors,
                self._on_task_drop,
                self._on_task_click,
                self._on_task_drag_start,
                self._on_new_task
            )
            column.frame.grid(row=0, column=i, sticky='nsew', padx=5, pady=5)
            self.columns[status.id] = column

        # Configure grid weights
        for i in range(len(statuses)):
            self.board_frame.columnconfigure(i, weight=1, minsize=280)
        self.board_frame.rowconfigure(0, weight=1)

        print(f"✅ Loaded {len(tasks)} tasks across {len(statuses)} columns")

    def _update_project_combo(self):
        """Update project filter combo box"""
        projects = self.project_controller.get_all_projects()
        project_names = ["All Projects"] + [p.name for p in projects]
        self.project_combo['values'] = project_names

    def _on_project_change(self, event):
        """Handle project filter change"""
        selected = self.project_var.get()

        if selected == "All Projects":
            self.current_filter.project_id = None
        else:
            projects = self.project_controller.get_all_projects()
            project = next((p for p in projects if p.name == selected), None)
            if project:
                self.current_filter.project_id = project.id

        self.load_data()

    def _on_task_click(self, task: Task):
        """Handle task click - open task details"""
        print(f"📋 Opening task: {task.title}")

        try:
            dialog = EnhancedTaskDialog(
                parent=self.parent_window.root,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=task
            )

            if dialog.result:
                # Task was updated, refresh board
                self.load_data()

        except Exception as e:
            print(f"❌ Error opening task: {e}")
            messagebox.showerror("Error", f"Failed to open task: {str(e)}")

    def _on_task_drag_start(self, task_card):
        """Handle start of task drag"""
        self.dragged_task = task_card

        # Create placeholder
        self.drag_placeholder = tk.Frame(
            task_card.parent,
            bg=self.colors['accent_gold'],
            height=task_card.winfo_height(),
            width=task_card.winfo_width()
        )

    def _on_task_drop(self, task: Task, new_status_id: int):
        """Handle task drop - update status"""
        if task.status_id == new_status_id:
            return  # No change needed

        print(f"📋 Moving task '{task.title}' to status {new_status_id}")

        try:
            # Update task status
            self.task_controller.update_task_status(
                task.id,
                new_status_id,
                self.parent_window.current_user.id if self.parent_window.current_user else None
            )

            # Refresh the board
            self.load_data()

            # Show feedback
            self.parent_window._update_status(f"Task moved: {task.title}")

        except Exception as e:
            print(f"❌ Error updating task status: {e}")
            messagebox.showerror("Error", f"Failed to update task: {str(e)}")
            # Refresh to restore original state
            self.load_data()

    def _on_new_task(self, status: TaskStatus):
        """Handle new task creation for specific status"""
        print(f"📋 Creating new task for status: {status.name}")

        try:
            # Pre-select the status in new task dialog
            dialog = EnhancedTaskDialog(
                parent=self.parent_window.root,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=None
            )

            # If we could pre-select status, that would be ideal
            # For now, user will need to select it manually

            if dialog.result:
                # Task was created, refresh board
                self.load_data()

        except Exception as e:
            print(f"❌ Error creating task: {e}")
            messagebox.showerror("Error", f"Failed to create task: {str(e)}")

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


class KanbanColumn:
    """Individual kanban column for a status"""

    def __init__(self, parent, status: TaskStatus, tasks: List[Task],
                 colors: dict, priority_colors: dict,
                 on_drop_callback, on_task_click_callback,
                 on_drag_start_callback, on_new_task_callback):
        self.parent = parent
        self.status = status
        self.tasks = tasks
        self.colors = colors
        self.priority_colors = priority_colors
        self.on_drop = on_drop_callback
        self.on_task_click = on_task_click_callback
        self.on_drag_start = on_drag_start_callback
        self.on_new_task = on_new_task_callback

        self.task_cards = []
        self.create_column()

    def create_column(self):
        """Create column UI"""
        # Column frame
        self.frame = tk.Frame(self.parent, bg=self.colors['bg_secondary'],
                              relief='flat', bd=1)

        # Header
        header_frame = tk.Frame(self.frame, bg=self.status.color or self.colors['bg_card'])
        header_frame.pack(fill=tk.X)

        # Status name and count
        header_content = tk.Frame(header_frame, bg=header_frame['bg'])
        header_content.pack(fill=tk.X, padx=10, pady=8)

        status_label = tk.Label(header_content,
                                text=self.status.name,
                                bg=header_frame['bg'],
                                fg='white',
                                font=('Segoe UI', 11, 'bold'))
        status_label.pack(side=tk.LEFT)

        count_label = tk.Label(header_content,
                               text=str(len(self.tasks)),
                               bg=header_frame['bg'],
                               fg='white',
                               font=('Segoe UI', 10))
        count_label.pack(side=tk.RIGHT)

        # Add task button
        add_btn = tk.Label(header_content,
                           text="➕",
                           bg=header_frame['bg'],
                           fg='white',
                           font=('Segoe UI', 12),
                           cursor='hand2')
        add_btn.pack(side=tk.RIGHT, padx=(0, 10))
        add_btn.bind("<Button-1>", lambda e: self.on_new_task(self.status))

        # Tasks container with scrollbar
        tasks_container = tk.Frame(self.frame, bg=self.colors['bg_secondary'])
        tasks_container.pack(fill=tk.BOTH, expand=True)

        # Canvas for scrolling
        self.canvas = tk.Canvas(tasks_container,
                                bg=self.colors['bg_secondary'],
                                highlightthickness=0,
                                width=260)

        scrollbar = ttk.Scrollbar(tasks_container, orient="vertical",
                                  command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_secondary'])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable drop zone
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        # Add tasks
        for task in self.tasks:
            self.add_task_card(task)

        # Empty state
        if not self.tasks:
            empty_label = tk.Label(self.scrollable_frame,
                                   text="Drop tasks here",
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_muted'],
                                   font=('Segoe UI', 9, 'italic'))
            empty_label.pack(pady=20)

    def add_task_card(self, task: Task):
        """Add a task card to the column"""
        card = DraggableTaskCard(
            self.scrollable_frame,
            task,
            self.colors,
            self.priority_colors,
            self.on_task_click,
            self.on_drag_start,
            lambda t: self.on_drop(t, self.status.id)
        )
        card.frame.pack(fill=tk.X, padx=5, pady=3)
        self.task_cards.append(card)

    def _on_canvas_click(self, event):
        """Handle click on canvas (for drag start)"""
        # Check if we clicked on a task card
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if widget:
            # Walk up the widget hierarchy to find a task card
            while widget and not hasattr(widget, 'task_card'):
                widget = widget.master

    def _on_canvas_drag(self, event):
        """Handle drag over canvas"""
        pass  # Drag visual feedback handled by task card

    def _on_canvas_release(self, event):
        """Handle drop on canvas"""
        # This is handled by the global drag system
        pass


class DraggableTaskCard:
    """Draggable task card widget"""

    def __init__(self, parent, task: Task, colors: dict, priority_colors: dict,
                 on_click_callback, on_drag_start_callback, on_drop_callback):
        self.parent = parent
        self.task = task
        self.colors = colors
        self.priority_colors = priority_colors
        self.on_click = on_click_callback
        self.on_drag_start = on_drag_start_callback
        self.on_drop = on_drop_callback

        self.dragging = False
        self.drag_data = {"x": 0, "y": 0}
        self.floating_card = None

        self.create_card()

    def create_card(self):
        """Create task card UI"""
        # Card frame
        self.frame = tk.Frame(self.parent, bg=self.colors['bg_card'],
                              relief='flat', bd=1, cursor='hand2')
        self.frame.task_card = self  # Reference for finding card from widget

        # Priority indicator
        priority_color = self.priority_colors.get(self.task.priority, self.colors['low'])
        priority_bar = tk.Frame(self.frame, bg=priority_color, width=4)
        priority_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Content
        content_frame = tk.Frame(self.frame, bg=self.colors['bg_card'])
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Issue type and ID
        header_frame = tk.Frame(content_frame, bg=self.colors['bg_card'])
        header_frame.pack(fill=tk.X)

        type_icon = "🐛" if self.task.issue_type == "BUG" else "✨" if self.task.issue_type == "FEATURE" else "📋"
        type_label = tk.Label(header_frame,
                              text=f"{type_icon} #{self.task.id}",
                              bg=self.colors['bg_card'],
                              fg=self.colors['text_secondary'],
                              font=('Segoe UI', 8))
        type_label.pack(side=tk.LEFT)

        # Title
        title_label = tk.Label(content_frame,
                               text=self.task.title,
                               bg=self.colors['bg_card'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 9, 'bold'),
                               wraplength=200,
                               justify=tk.LEFT)
        title_label.pack(fill=tk.X, pady=(2, 4))

        # Details
        details_frame = tk.Frame(content_frame, bg=self.colors['bg_card'])
        details_frame.pack(fill=tk.X)

        # Module
        if self.task.module_name:
            module_label = tk.Label(details_frame,
                                    text=self.task.module_name,
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_secondary'],
                                    font=('Segoe UI', 8),
                                    padx=6,
                                    pady=2)
            module_label.pack(side=tk.LEFT, padx=(0, 4))

        # Assignee
        if self.task.assignee_name:
            assignee_label = tk.Label(details_frame,
                                      text=f"👤 {self.task.assignee_name}",
                                      bg=self.colors['bg_card'],
                                      fg=self.colors['text_secondary'],
                                      font=('Segoe UI', 8))
            assignee_label.pack(side=tk.LEFT)

        # Bind events
        self._bind_drag_events()

        # Click event (not on drag)
        def on_click(event):
            if not self.dragging:
                self.on_click(self.task)

        self.frame.bind("<Button-1>", on_click)

    def _bind_drag_events(self):
        """Bind drag and drop events to all widgets in card"""
        widgets = self._get_all_widgets(self.frame)

        for widget in widgets:
            widget.bind("<Button-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)
            widget.bind("<ButtonRelease-1>", self._on_drag_release)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _get_all_widgets(self, parent):
        """Get all child widgets recursively"""
        widgets = [parent]
        for child in parent.winfo_children():
            widgets.extend(self._get_all_widgets(child))
        return widgets

    def _on_enter(self, event):
        """Mouse enter effect"""
        if not self.dragging:
            self.frame.configure(bg=self.colors['bg_hover'])

    def _on_leave(self, event):
        """Mouse leave effect"""
        if not self.dragging:
            self.frame.configure(bg=self.colors['bg_card'])

    def _on_drag_start(self, event):
        """Start dragging"""
        self.dragging = False  # Will be set to True only if we actually move
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root

    def _on_drag_motion(self, event):
        """Handle drag motion"""
        # Check if we've moved enough to start dragging
        if not self.dragging:
            if abs(event.x_root - self.drag_data["x"]) > 5 or \
                    abs(event.y_root - self.drag_data["y"]) > 5:
                self.dragging = True
                self._start_drag()

        if self.dragging and self.floating_card:
            # Move floating card
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]

            self.floating_card.place(x=self.frame.winfo_rootx() + x,
                                     y=self.frame.winfo_rooty() + y)

    def _on_drag_release(self, event):
        """Handle drag release"""
        if self.dragging:
            self._end_drag(event)
        self.dragging = False

    def _start_drag(self):
        """Start drag operation"""
        self.on_drag_start(self)

        # Hide original card
        self.frame.pack_forget()

        # Create floating card
        self.floating_card = tk.Toplevel(self.frame)
        self.floating_card.overrideredirect(True)
        self.floating_card.attributes('-alpha', 0.8)

        # Copy card appearance
        floating_frame = tk.Frame(self.floating_card, bg=self.colors['bg_card'],
                                  relief='raised', bd=2)
        floating_frame.pack()

        # Simple content
        tk.Label(floating_frame,
                 text=self.task.title,
                 bg=self.colors['bg_card'],
                 fg=self.colors['text_primary'],
                 font=('Segoe UI', 9, 'bold'),
                 padx=10,
                 pady=5).pack()

    def _end_drag(self, event):
        """End drag operation"""
        if self.floating_card:
            # Find target column
            target_widget = event.widget.winfo_containing(event.x_root, event.y_root)

            # Walk up to find kanban column
            while target_widget:
                if hasattr(target_widget, 'master') and hasattr(target_widget.master, 'status'):
                    # Found a column
                    target_column = target_widget.master
                    if hasattr(target_column, 'status'):
                        self.on_drop(self.task)
                        break

                # Check parent
                if hasattr(target_widget, 'master'):
                    target_widget = target_widget.master

                    # Also check if we found a canvas that's part of a column
                    if isinstance(target_widget, tk.Canvas):
                        # Check if canvas parent has status
                        canvas_parent = target_widget.master
                        if canvas_parent:
                            column_parent = canvas_parent.master
                            if column_parent and hasattr(column_parent, 'frame'):
                                # Search in parent's children for column
                                for col_id, col in self.parent.master.master.master.columns.items():
                                    if col.canvas == target_widget:
                                        col.on_drop(self.task, col.status.id)
                                        break
                else:
                    break

            # Destroy floating card
            self.floating_card.destroy()
            self.floating_card = None

        # Restore original card
        self.frame.pack(fill=tk.X, padx=5, pady=3)