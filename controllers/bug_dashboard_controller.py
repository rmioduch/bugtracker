"""
Bug Dashboard Controller - Enhanced dashboard for TaskMaster BugTracker
POPRAWIONA WERSJA v3 - DZIAŁAJĄCE FILTROWANIE
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict
import math

from models.database import DatabaseManager
from models.entities import (
    Task, User, Module, SearchFilter, DashboardMetrics,
    ISSUE_TYPE_CHOICES, PRIORITY_CHOICES, SEVERITY_CHOICES, MODULE_CHOICES
)
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from utils.helpers import format_date

# IMPORTANT: Import the dialog for viewing/editing tasks
try:
    from views.enhanced_task_dialog import EnhancedTaskDialog
except ImportError:
    print("⚠️ Warning: Could not import EnhancedTaskDialog")
    EnhancedTaskDialog = None


class BugDashboardController:
    """Enhanced dashboard controller - POPRAWIONA WERSJA v3 z działającym filtrowaniem"""

    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.db_manager = DatabaseManager()
        self.task_controller = TaskController()
        self.project_controller = ProjectController()

        # Current user (in real app, this would come from session)
        self.current_user_id = 1  # Default admin user

        # NOWE - aktualny filtr dla dashboardu
        self.current_filter = SearchFilter()

        # Dashboard data
        self.metrics = None
        self.recent_tasks = []
        self.filtered_tasks = []  # NOWE - przefiltrowane zadania

        # Widget references for safe cleanup
        self.canvas_widget = None
        self.scrollable_frame = None
        self.parent_frame = None

        # Chart widgets for dynamic resizing
        self.module_chart_canvas = None
        self.priority_chart_canvas = None

        # Colors for charts (Money Mentor AI theme)
        self.colors = {
            'bg_primary': '#1a222c',
            'bg_secondary': '#2d3748',
            'bg_card': '#374151',
            'text_primary': '#f7fafc',
            'text_secondary': '#cbd5e0',
            'accent_gold': '#E8C547',
            'accent_teal': '#00BFA6',
            'accent_purple': '#9F7AEA',
            'critical': '#EF4444',
            'high': '#F59E0B',
            'medium': '#10B981',
            'low': '#6B7280'
        }

    def update_filter(self, search_filter: SearchFilter):
        """NOWA METODA - Aktualizuj filtr i odśwież dashboard"""
        print(f"📊 Dashboard: Otrzymano nowy filtr: {search_filter}")

        self.current_filter = search_filter
        self._refresh_dashboard_data()

        print(f"✅ Dashboard: Filtr zastosowany i dane odświeżone")

    def clear_filter(self):
        """NOWA METODA - Wyczyść filtr i pokaż wszystkie dane"""
        print("🔄 Dashboard: Czyszczenie filtrów")

        self.current_filter = SearchFilter()
        self._refresh_dashboard_data()

        print("✅ Dashboard: Filtry wyczyszczone")

    def create_dashboard_view(self, parent_frame):
        """Create the complete dashboard view - POPRAWIONA WERSJA v3"""
        print("🎨 Creating IMPROVED dashboard view v3 z filtrowaniem...")

        try:
            # Clean up previous event handlers
            self._cleanup_event_handlers()

            # Clear existing content
            for widget in parent_frame.winfo_children():
                widget.destroy()

            # Store parent frame reference for resizing
            self.parent_frame = parent_frame

            # Main container
            main_frame = tk.Frame(parent_frame, bg=self.colors['bg_primary'])
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Compact dashboard header z informacją o filtrach
            self._create_compact_header_with_filter_info(main_frame)

            # Main content area (scrollable) - IMPROVED
            self._create_improved_scrollable_content(main_frame)

            # Load initial data z uwzględnieniem filtrów
            self._refresh_dashboard_data()

            # KLUCZOWE - force update scroll region po załadowaniu danych
            parent_frame.after(100, self._force_scroll_update)

            # Bind resize event
            parent_frame.bind("<Configure>", self._on_resize)

            print("✅ IMPROVED dashboard view v3 created successfully z filtrowaniem")

        except Exception as e:
            print(f"❌ Error creating dashboard: {e}")
            import traceback
            traceback.print_exc()

    def _create_compact_header_with_filter_info(self, parent):
        """Create compact dashboard header z informacją o aktywnych filtrach"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(3, 5))

        # Left side - title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT, padx=(8, 0))

        title_label = tk.Label(title_frame,
                               text="🐛 Bug Tracker Dashboard",
                               bg=self.colors['bg_primary'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor='w')

        # NOWE - informacja o aktywnych filtrach
        filter_info = self._get_filter_info()
        subtitle_label = tk.Label(title_frame,
                                  text=filter_info,
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_secondary'],
                                  font=('Segoe UI', 10))
        subtitle_label.pack(anchor='w')

        # Right side - quick actions
        actions_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        actions_frame.pack(side=tk.RIGHT, padx=(0, 8))

        self._create_compact_action_button(actions_frame, "🔄 Refresh", self._refresh_dashboard_data, self.colors['accent_purple'])

        # NOWE - przycisk czyszczenia filtrów
        if self._has_active_filters():
            self._create_compact_action_button(actions_frame, "🗑️ Clear Filters", self.clear_filter, self.colors['critical'])

    def _get_filter_info(self) -> str:
        """NOWA METODA - Zwróć informację o aktywnych filtrach"""
        if not self._has_active_filters():
            return "Issue Management - All Data"

        info_parts = []

        if self.current_filter.project_id:
            try:
                projects = self.project_controller.get_all_projects()
                project = next((p for p in projects if p.id == self.current_filter.project_id), None)
                if project:
                    info_parts.append(f"Project: {project.name}")
            except:
                pass

        if self.current_filter.issue_type:
            type_display = dict(ISSUE_TYPE_CHOICES).get(self.current_filter.issue_type, self.current_filter.issue_type)
            info_parts.append(f"Type: {type_display}")

        if self.current_filter.priority:
            priority_display = dict(PRIORITY_CHOICES).get(self.current_filter.priority, f"Priority {self.current_filter.priority}")
            info_parts.append(f"{priority_display}")

        if self.current_filter.assignee_id:
            if self.current_filter.assignee_id == self.current_user_id:
                info_parts.append("My Issues")
            else:
                info_parts.append("Assigned Issues")

        if self.current_filter.module_id:
            try:
                modules = self.db_manager.get_all_modules()
                module = next((m for m in modules if m.id == self.current_filter.module_id), None)
                if module:
                    info_parts.append(f"Module: {module.display_name}")
            except:
                pass

        return f"Filtered: {' | '.join(info_parts)}"

    def _has_active_filters(self) -> bool:
        """NOWA METODA - Sprawdź czy są aktywne filtry"""
        return (self.current_filter.project_id is not None or
                self.current_filter.issue_type is not None or
                self.current_filter.priority is not None or
                self.current_filter.assignee_id is not None or
                self.current_filter.module_id is not None or
                self.current_filter.status_id is not None or
                self.current_filter.query is not None)

    def _force_scroll_update(self):
        """Force update scroll region - FIX dla problemu z Recent Activity"""
        try:
            if self.canvas_widget and self.canvas_widget.winfo_exists():
                # Update scroll region
                self.canvas_widget.update_idletasks()
                self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all"))

                # Ensure we're scrolled to top
                self.canvas_widget.yview_moveto(0)

                print("✅ Scroll region force updated")
        except Exception as e:
            print(f"⚠️ Force scroll update error: {e}")

    def _on_resize(self, event):
        """Handle window resize - update chart sizes"""
        try:
            if event.widget == self.parent_frame:
                self.parent_frame.after_idle(self._update_chart_sizes)
        except Exception as e:
            print(f"⚠️ Resize handler error: {e}")

    def _update_chart_sizes(self):
        """Update chart canvas sizes based on available space"""
        try:
            if not (self.module_chart_canvas and self.priority_chart_canvas):
                return

            # Get available width from parent
            available_width = self.parent_frame.winfo_width()

            # Calculate compact chart width
            if available_width > 100:
                chart_width = max(250, (available_width - 80) // 2)
                chart_height = max(180, int(chart_width * 0.7))

                # Update canvas sizes
                self.module_chart_canvas.configure(width=chart_width, height=chart_height)
                self.priority_chart_canvas.configure(width=chart_width, height=chart_height)

                # Redraw charts with new sizes
                self._redraw_charts()

        except Exception as e:
            print(f"⚠️ Chart resize error: {e}")

    def _cleanup_event_handlers(self):
        """Safely clean up event handlers"""
        try:
            # Reset references
            self.canvas_widget = None
            self.module_chart_canvas = None
            self.priority_chart_canvas = None

        except Exception as e:
            print(f"⚠️ Warning during cleanup: {e}")

    def _create_compact_action_button(self, parent, text, command, color):
        """Create styled compact action button"""
        btn = tk.Label(parent,
                       text=text,
                       bg=color,
                       fg='white',
                       font=('Segoe UI', 9, 'bold'),
                       padx=12,
                       pady=6,
                       cursor='hand2')
        btn.pack(side=tk.RIGHT, padx=3)

        # Hover effects
        def on_enter(e):
            btn.configure(bg=self._darken_color(color))
        def on_leave(e):
            btn.configure(bg=color)
        def on_click(e):
            command()

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)

        return btn

    def _create_improved_scrollable_content(self, parent):
        """Create IMPROVED scrollable main content area - FIX dla Recent Activity"""
        # Create canvas and scrollbar
        self.canvas_widget = tk.Canvas(parent, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas_widget.yview)
        self.scrollable_frame = tk.Frame(self.canvas_widget, bg=self.colors['bg_primary'])

        # Configure scrolling - IMPROVED
        def configure_scroll_region(event=None):
            # KLUCZOWE - zawsze aktualizuj scroll region
            self.canvas_widget.update_idletasks()
            self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all"))

        def configure_canvas_width(event):
            canvas_width = event.width
            self.canvas_widget.itemconfig(self.canvas_window, width=canvas_width)
            # DODANE - aktualizuj scroll region też przy zmianie szerokości
            self.canvas_widget.after_idle(configure_scroll_region)

        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        self.canvas_widget.bind("<Configure>", configure_canvas_width)

        self.canvas_window = self.canvas_widget.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_widget.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # NAPRAWIONE SCROLLOWANIE KÓŁKIEM MYSZKI
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass
            except Exception as e:
                print(f"⚠️ Mousewheel error: {e}")

        # Bind mouse wheel do wszystkich kluczowych elementów
        self.canvas_widget.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        parent.bind("<MouseWheel>", _on_mousewheel)

        # Ensure focus for scrolling
        self.canvas_widget.focus_set()

        # Create compact dashboard sections
        self._create_compact_metrics_section()
        self._create_improved_charts_section()
        self._create_compact_recent_activity_section()
        self._create_compact_quick_filters_section()

        # KLUCZOWE - force update po utworzeniu wszystkich sekcji
        self.canvas_widget.after(50, configure_scroll_region)

    def _create_compact_metrics_section(self):
        """Create compact key metrics cards"""
        metrics_frame = tk.LabelFrame(self.scrollable_frame,
                                      text="📊 Key Metrics",
                                      bg=self.colors['bg_secondary'],
                                      fg=self.colors['text_primary'],
                                      font=('Segoe UI', 11, 'bold'),
                                      bd=0)
        metrics_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        # Cards container
        cards_frame = tk.Frame(metrics_frame, bg=self.colors['bg_secondary'])
        cards_frame.pack(fill=tk.X, padx=10, pady=10)

        # Create compact metric cards
        self.metric_cards = {}

        self.metric_cards['total'] = self._create_compact_metric_card(
            cards_frame, "Total Issues", "0", "📋", self.colors['accent_teal']
        )

        self.metric_cards['open'] = self._create_compact_metric_card(
            cards_frame, "Open Issues", "0", "🔓", self.colors['accent_purple']
        )

        self.metric_cards['critical'] = self._create_compact_metric_card(
            cards_frame, "Critical Bugs", "0", "🔴", self.colors['critical']
        )

        self.metric_cards['my_assigned'] = self._create_compact_metric_card(
            cards_frame, "My Assigned", "0", "👤", self.colors['accent_gold']
        )

    def _create_compact_metric_card(self, parent, title, value, icon, color):
        """Create compact individual metric card"""
        card_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1)
        card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)

        # Card header with icon
        header_frame = tk.Frame(card_frame, bg=color, height=8)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Content - COMPACT PADDING
        content_frame = tk.Frame(card_frame, bg=self.colors['bg_card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Icon and title
        title_frame = tk.Frame(content_frame, bg=self.colors['bg_card'])
        title_frame.pack(fill=tk.X)

        icon_label = tk.Label(title_frame,
                              text=icon,
                              bg=self.colors['bg_card'],
                              fg=color,
                              font=('Segoe UI', 16))
        icon_label.pack(side=tk.LEFT)

        title_label = tk.Label(title_frame,
                               text=title,
                               bg=self.colors['bg_card'],
                               fg=self.colors['text_secondary'],
                               font=('Segoe UI', 9))
        title_label.pack(side=tk.LEFT, padx=(8, 0))

        # Value
        value_label = tk.Label(content_frame,
                               text=value,
                               bg=self.colors['bg_card'],
                               fg=self.colors['text_primary'],
                               font=('Segoe UI', 24, 'bold'))
        value_label.pack(pady=(8, 0))

        # Bind mouse wheel to card elements
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        for widget in [card_frame, content_frame, title_frame, icon_label, title_label, value_label]:
            widget.bind("<MouseWheel>", _on_mousewheel)

        return {
            'frame': card_frame,
            'value_label': value_label,
            'color': color
        }

    def _create_improved_charts_section(self):
        """Create IMPROVED charts section - legenda z boku"""
        charts_frame = tk.LabelFrame(self.scrollable_frame,
                                     text="📈 Analytics",
                                     bg=self.colors['bg_secondary'],
                                     fg=self.colors['text_primary'],
                                     font=('Segoe UI', 11, 'bold'),
                                     bd=0)
        charts_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        # Charts container
        charts_container = tk.Frame(charts_frame, bg=self.colors['bg_secondary'])
        charts_container.pack(fill=tk.X, padx=10, pady=10)

        # Issues by Module chart (left) - ZMIENIONE dla legendy z boku
        self.module_chart_frame = tk.Frame(charts_container, bg=self.colors['bg_card'])
        self.module_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        # Issues by Priority chart (right)
        self.priority_chart_frame = tk.Frame(charts_container, bg=self.colors['bg_card'])
        self.priority_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        # Bind mouse wheel to chart frames
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        charts_frame.bind("<MouseWheel>", _on_mousewheel)
        charts_container.bind("<MouseWheel>", _on_mousewheel)
        self.module_chart_frame.bind("<MouseWheel>", _on_mousewheel)
        self.priority_chart_frame.bind("<MouseWheel>", _on_mousewheel)

    def _create_compact_recent_activity_section(self):
        """Create compact recent activity section"""
        activity_frame = tk.LabelFrame(self.scrollable_frame,
                                       text="🕒 Recent Activity",
                                       bg=self.colors['bg_secondary'],
                                       fg=self.colors['text_primary'],
                                       font=('Segoe UI', 11, 'bold'),
                                       bd=0)
        activity_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        # Activity list
        self.activity_list_frame = tk.Frame(activity_frame, bg=self.colors['bg_secondary'])
        self.activity_list_frame.pack(fill=tk.X, padx=10, pady=10)

        # Bind mouse wheel
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        activity_frame.bind("<MouseWheel>", _on_mousewheel)
        self.activity_list_frame.bind("<MouseWheel>", _on_mousewheel)

    def _create_compact_quick_filters_section(self):
        """Create compact quick filters section"""
        filters_frame = tk.LabelFrame(self.scrollable_frame,
                                      text="🔍 Quick Filters",
                                      bg=self.colors['bg_secondary'],
                                      fg=self.colors['text_primary'],
                                      font=('Segoe UI', 11, 'bold'),
                                      bd=0)
        filters_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        # Filters container
        filters_container = tk.Frame(filters_frame, bg=self.colors['bg_secondary'])
        filters_container.pack(fill=tk.X, padx=10, pady=10)

        # Top row
        top_row = tk.Frame(filters_container, bg=self.colors['bg_secondary'])
        top_row.pack(fill=tk.X, pady=(0, 5))

        # Bottom row
        bottom_row = tk.Frame(filters_container, bg=self.colors['bg_secondary'])
        bottom_row.pack(fill=tk.X)

        # Top row filters
        self._create_compact_filter_button(top_row, "🐛 All Bugs",
                                           lambda: self._apply_quick_filter({'issue_type': 'BUG'}))

        self._create_compact_filter_button(top_row, "🔴 Critical Issues",
                                           lambda: self._apply_quick_filter({'priority': 1}))

        self._create_compact_filter_button(top_row, "📈 Trading Module",
                                           lambda: self._apply_quick_filter({'module_name': 'TRADING'}))

        # Bottom row filters
        self._create_compact_filter_button(bottom_row, "👤 My Issues",
                                           lambda: self._apply_quick_filter({'assignee_id': self.current_user_id}))

        self._create_compact_filter_button(bottom_row, "🔓 Open Issues",
                                           lambda: self._apply_quick_filter({'status_open': True}))

        self._create_compact_filter_button(bottom_row, "✨ Feature Requests",
                                           lambda: self._apply_quick_filter({'issue_type': 'FEATURE'}))

        # Bind mouse wheel
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        filters_frame.bind("<MouseWheel>", _on_mousewheel)
        filters_container.bind("<MouseWheel>", _on_mousewheel)
        top_row.bind("<MouseWheel>", _on_mousewheel)
        bottom_row.bind("<MouseWheel>", _on_mousewheel)

    def _create_compact_filter_button(self, parent, text, command):
        """Create compact quick filter button"""
        btn = tk.Label(parent,
                       text=text,
                       bg=self.colors['bg_card'],
                       fg=self.colors['text_primary'],
                       font=('Segoe UI', 9),
                       padx=12,
                       pady=8,
                       cursor='hand2',
                       relief='flat',
                       bd=1)
        btn.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)

        # Hover effects
        def on_enter(e):
            btn.configure(bg=self.colors['accent_gold'], fg='black')
        def on_leave(e):
            btn.configure(bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        def on_click(e):
            command()
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)
        btn.bind("<MouseWheel>", _on_mousewheel)

    def _refresh_dashboard_data(self):
        """POPRAWIONA METODA - Refresh all dashboard data z uwzględnieniem filtrów"""
        print("🔄 Refreshing dashboard data z filtrowaniem...")

        try:
            # NOWE - pobierz przefiltrowane zadania
            self.filtered_tasks = self.task_controller.search_tasks_advanced(self.current_filter)
            print(f"📊 Znaleziono {len(self.filtered_tasks)} przefiltrowanych zadań")

            # NOWE - oblicz metryki na podstawie przefiltrowanych danych
            self.metrics = self._calculate_filtered_metrics()

            # Update metric cards
            self._update_metric_cards()

            # Update charts
            self._update_improved_charts()

            # Update recent activity z przefiltrowanych danych
            self._update_compact_recent_activity()

            # KLUCZOWE - force scroll update po refreshu danych
            self.canvas_widget.after(100, self._force_scroll_update)

            print("✅ Dashboard data refreshed z filtrowaniem")

        except Exception as e:
            print(f"❌ Error refreshing dashboard: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to refresh dashboard: {str(e)}")

    def _calculate_filtered_metrics(self) -> DashboardMetrics:
        """NOWA METODA - Oblicz metryki na podstawie przefiltrowanych danych"""
        metrics = DashboardMetrics()

        if not self.filtered_tasks:
            return metrics

        # Podstawowe liczby
        metrics.total_issues = len(self.filtered_tasks)

        # Otwarte vs zamknięte
        open_statuses = ["📋 To Do", "🚀 In Progress", "👀 Review", "🔒 Blocked",
                         "🔍 Triaged", "👀 Code Review", "🧪 Testing", "🔄 Reopened"]

        metrics.open_issues = len([t for t in self.filtered_tasks if t.status_name in open_statuses])
        metrics.closed_issues = metrics.total_issues - metrics.open_issues

        # Krytyczne bugi
        metrics.critical_bugs = len([t for t in self.filtered_tasks
                                     if t.issue_type == 'BUG' and t.priority == 1])

        # Moje przypisane
        if self.current_user_id:
            metrics.my_assigned = len([t for t in self.filtered_tasks
                                       if t.assignee_id == self.current_user_id and t.status_name in open_statuses])

        # Zadania według modułów
        module_counts = {}
        for task in self.filtered_tasks:
            module = task.module_name or 'Nie przypisano'
            module_counts[module] = module_counts.get(module, 0) + 1
        metrics.issues_by_module = module_counts

        # Zadania według statusów
        status_counts = {}
        for task in self.filtered_tasks:
            status = task.status_name or 'Unknown'
            status_counts[status] = status_counts.get(status, 0) + 1
        metrics.issues_by_status = status_counts

        print(f"📊 Metryki: {metrics.total_issues} zadań, {metrics.open_issues} otwartych, {metrics.critical_bugs} krytycznych")
        return metrics

    def _update_metric_cards(self):
        """Update metric card values"""
        if not self.metrics:
            return

        self.metric_cards['total']['value_label'].configure(text=str(self.metrics.total_issues))
        self.metric_cards['open']['value_label'].configure(text=str(self.metrics.open_issues))
        self.metric_cards['critical']['value_label'].configure(text=str(self.metrics.critical_bugs))
        self.metric_cards['my_assigned']['value_label'].configure(text=str(self.metrics.my_assigned))

    def _update_improved_charts(self):
        """Update dashboard charts - IMPROVED VERSION z legendą z boku"""
        if not self.metrics:
            return

        # Clear existing charts
        for widget in self.module_chart_frame.winfo_children():
            widget.destroy()
        for widget in self.priority_chart_frame.winfo_children():
            widget.destroy()

        # Calculate compact chart size
        try:
            frame_width = self.module_chart_frame.winfo_width()
            if frame_width <= 1:
                frame_width = 300

            chart_width = max(250, frame_width - 30)
            chart_height = max(180, int(chart_width * 0.7))
        except:
            chart_width, chart_height = 300, 210

        # Issues by Module chart
        self._create_improved_pie_chart(
            self.module_chart_frame,
            "Issues by Module",
            self.metrics.issues_by_module,
            chart_width,
            chart_height
        )

        # NOWE - Issues by Priority chart na podstawie przefiltrowanych danych
        priority_data = self._calculate_priority_distribution()

        self._create_compact_bar_chart(
            self.priority_chart_frame,
            "Issues by Priority",
            priority_data,
            chart_width,
            chart_height
        )

    def _calculate_priority_distribution(self) -> Dict[str, int]:
        """NOWA METODA - Oblicz rozkład priorytetów z przefiltrowanych danych"""
        priority_counts = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'Trivial': 0
        }

        for task in self.filtered_tasks:
            if task.priority == 1:
                priority_counts['Critical'] += 1
            elif task.priority == 2:
                priority_counts['High'] += 1
            elif task.priority == 3:
                priority_counts['Medium'] += 1
            elif task.priority == 4:
                priority_counts['Low'] += 1
            elif task.priority == 5:
                priority_counts['Trivial'] += 1

        return priority_counts

    def _create_improved_pie_chart(self, parent, title, data, width, height):
        """Create improved pie chart - LEGENDA Z BOKU"""
        # Chart header
        header_label = tk.Label(parent, text=title,
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_primary'],
                                font=('Segoe UI', 12, 'bold'))
        header_label.pack(pady=(10, 5))

        # Get top 5 items
        sorted_data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:5])

        if not sorted_data or sum(sorted_data.values()) == 0:
            no_data_label = tk.Label(parent, text="No data available",
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text_secondary'],
                                     font=('Segoe UI', 11))
            no_data_label.pack(pady=20)
            return

        # NOWY LAYOUT - wykres i legenda obok siebie
        chart_container = tk.Frame(parent, bg=self.colors['bg_card'])
        chart_container.pack(fill=tk.BOTH, expand=True, pady=5)

        # LEFT - Canvas for pie chart
        chart_left_frame = tk.Frame(chart_container, bg=self.colors['bg_card'])
        chart_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Adjust chart size for side legend
        chart_canvas_width = int(width * 0.55)  # 65% szerokości dla wykresu
        chart_canvas_height = int(height * 0.85)  # 85% wysokości

        self.module_chart_canvas = tk.Canvas(chart_left_frame,
                                             width=chart_canvas_width,
                                             height=chart_canvas_height,
                                             bg=self.colors['bg_card'],
                                             highlightthickness=0)
        self.module_chart_canvas.pack(pady=5)

        # Draw pie chart
        total = sum(sorted_data.values())
        colors = [self.colors['accent_teal'], self.colors['accent_purple'],
                  self.colors['accent_gold'], self.colors['critical'], self.colors['high']]

        center_x, center_y = chart_canvas_width // 2, chart_canvas_height // 2
        radius = min(chart_canvas_width, chart_canvas_height) // 3
        start_angle = 0

        for i, (label, value) in enumerate(sorted_data.items()):
            if value > 0:
                angle = (value / total) * 360
                color = colors[i % len(colors)]

                self.module_chart_canvas.create_arc(center_x - radius, center_y - radius,
                                                    center_x + radius, center_y + radius,
                                                    start=start_angle, extent=angle,
                                                    fill=color, outline=color, width=2)
                start_angle += angle

        # RIGHT - PIONOWA legenda z boku
        legend_right_frame = tk.Frame(chart_container, bg=self.colors['bg_card'])
        legend_right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 5))

        # Legenda title
        legend_title = tk.Label(legend_right_frame, text="Modules:",
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_secondary'],
                                font=('Segoe UI', 9, 'bold'))
        legend_title.pack(pady=(15, 8))

        # Legend items - PIONOWO
        for i, (label, value) in enumerate(sorted_data.items()):
            if value > 0:
                color = colors[i % len(colors)]

                item_frame = tk.Frame(legend_right_frame, bg=self.colors['bg_card'])
                item_frame.pack(fill=tk.X, pady=2)

                # Color indicator
                color_box = tk.Label(item_frame, text="●", fg=color,
                                     bg=self.colors['bg_card'], font=('Segoe UI', 12))
                color_box.pack(side=tk.LEFT)

                # Label and value - WIELOLINIOWY dla długich nazw
                label_text = f"{label[:12]}" if len(label) > 12 else label
                value_text = f"\n{value} issues"

                label_widget = tk.Label(item_frame,
                                        text=f"{label_text}{value_text}",
                                        bg=self.colors['bg_card'],
                                        fg=self.colors['text_primary'],
                                        font=('Segoe UI', 8),
                                        justify=tk.LEFT)
                label_widget.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Bind mouse wheel to chart elements
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        self.module_chart_canvas.bind("<MouseWheel>", _on_mousewheel)
        chart_container.bind("<MouseWheel>", _on_mousewheel)
        legend_right_frame.bind("<MouseWheel>", _on_mousewheel)

    def _create_compact_bar_chart(self, parent, title, data, width, height):
        """Create compact bar chart"""
        # Chart header
        header_label = tk.Label(parent, text=title,
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_primary'],
                                font=('Segoe UI', 12, 'bold'))
        header_label.pack(pady=(10, 5))

        if not data or sum(data.values()) == 0:
            no_data_label = tk.Label(parent, text="No data available",
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text_secondary'],
                                     font=('Segoe UI', 11))
            no_data_label.pack(pady=20)
            return

        # Canvas for bar chart
        self.priority_chart_canvas = tk.Canvas(parent, width=width, height=height,
                                               bg=self.colors['bg_card'], highlightthickness=0)
        self.priority_chart_canvas.pack(pady=8)

        # Chart dimensions
        margin = max(20, width // 20)
        chart_width = width - 2 * margin
        chart_height = height - 2 * margin

        max_value = max(data.values()) if data.values() else 1
        bar_width = chart_width / len(data)

        colors = [self.colors['critical'], self.colors['high'], self.colors['medium'],
                  self.colors['low'], self.colors['text_secondary']]

        # Draw bars
        for i, (label, value) in enumerate(data.items()):
            if max_value > 0:
                bar_height = (value / max_value) * chart_height

                x1 = margin + i * bar_width + bar_width * 0.1
                y1 = margin + chart_height - bar_height
                x2 = x1 + bar_width * 0.8
                y2 = margin + chart_height

                color = colors[i % len(colors)]

                self.priority_chart_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

                if value > 0:
                    self.priority_chart_canvas.create_text((x1 + x2) / 2, y1 - 8, text=str(value),
                                                           fill=self.colors['text_primary'],
                                                           font=('Segoe UI', 8, 'bold'))

        # Compact legend
        legend_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        legend_frame.pack(pady=5)

        for i, (label, value) in enumerate(data.items()):
            color = colors[i % len(colors)]

            item_frame = tk.Frame(legend_frame, bg=self.colors['bg_card'])
            item_frame.pack(side=tk.LEFT, padx=5)

            color_box = tk.Label(item_frame, text="■", fg=color,
                                 bg=self.colors['bg_card'], font=('Segoe UI', 9))
            color_box.pack()

            label_widget = tk.Label(item_frame, text=label[:5],  # Skrócone etykiety
                                    bg=self.colors['bg_card'],
                                    fg=self.colors['text_primary'],
                                    font=('Segoe UI', 7))
            label_widget.pack()

        # Bind mouse wheel
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        self.priority_chart_canvas.bind("<MouseWheel>", _on_mousewheel)
        legend_frame.bind("<MouseWheel>", _on_mousewheel)

    def _redraw_charts(self):
        """Redraw charts with current data and new sizes"""
        if self.metrics:
            self._update_improved_charts()

    def _update_compact_recent_activity(self):
        """POPRAWIONA METODA - Update compact recent activity list z przefiltrowanych danych"""
        # Clear existing activity
        for widget in self.activity_list_frame.winfo_children():
            widget.destroy()

        # Używaj przefiltrowanych zadań zamiast pobierać wszystkie
        recent_tasks = self.filtered_tasks[:6] if self.filtered_tasks else []

        if not recent_tasks:
            no_activity_label = tk.Label(self.activity_list_frame,
                                         text="No matching activities" if self._has_active_filters() else "No recent activity",
                                         bg=self.colors['bg_secondary'],
                                         fg=self.colors['text_secondary'],
                                         font=('Segoe UI', 11))
            no_activity_label.pack(pady=20)
            return

        for task in recent_tasks:
            self._create_compact_activity_item(task)

    def _create_compact_activity_item(self, task: Task):
        """Create compact activity item widget"""
        item_frame = tk.Frame(self.activity_list_frame, bg=self.colors['bg_card'],
                              relief='flat', bd=1)
        item_frame.pack(fill=tk.X, pady=2)

        # Left side - issue info
        info_frame = tk.Frame(item_frame, bg=self.colors['bg_card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Issue type icon and title
        title_frame = tk.Frame(info_frame, bg=self.colors['bg_card'])
        title_frame.pack(fill=tk.X)

        type_icon = "🐛" if task.issue_type == "BUG" else "✨" if task.issue_type == "FEATURE" else "📋"

        icon_label = tk.Label(title_frame, text=type_icon, bg=self.colors['bg_card'],
                              fg=self.colors['accent_teal'], font=('Segoe UI', 12))
        icon_label.pack(side=tk.LEFT)

        title_label = tk.Label(title_frame, text=task.title, bg=self.colors['bg_card'],
                               fg=self.colors['text_primary'], font=('Segoe UI', 10, 'bold'))
        title_label.pack(side=tk.LEFT, padx=(8, 0))

        # Details
        details_text = f"#{task.id} • {task.get_priority_display()} • {task.module_name or 'No Module'}"
        if task.assignee_name:
            details_text += f" • Assigned to {task.assignee_name}"

        details_label = tk.Label(info_frame, text=details_text, bg=self.colors['bg_card'],
                                 fg=self.colors['text_secondary'], font=('Segoe UI', 8))
        details_label.pack(fill=tk.X, pady=(3, 0))

        # Right side - status and date
        status_frame = tk.Frame(item_frame, bg=self.colors['bg_card'])
        status_frame.pack(side=tk.RIGHT, padx=12, pady=8)

        status_label = tk.Label(status_frame, text=task.status_name, bg=self.colors['accent_purple'],
                                fg='white', font=('Segoe UI', 8, 'bold'), padx=8, pady=4)
        status_label.pack()

        if task.updated_at:
            date_label = tk.Label(status_frame, text=format_date(task.updated_at),
                                  bg=self.colors['bg_card'], fg=self.colors['text_secondary'],
                                  font=('Segoe UI', 7))
            date_label.pack(pady=(4, 0))

        # Click handler
        def on_click(event):
            self._view_task_details(task)

        # Bind mouse wheel and click to all elements
        def _on_mousewheel(event):
            try:
                if self.canvas_widget and self.canvas_widget.winfo_exists():
                    self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        for widget in [item_frame, info_frame, title_frame, icon_label, title_label, details_label, status_frame, status_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.configure(cursor='hand2')

        if task.updated_at:
            date_label.bind("<Button-1>", on_click)
            date_label.bind("<MouseWheel>", _on_mousewheel)
            date_label.configure(cursor='hand2')

    def _new_bug(self):
        """Create new bug report"""
        print("🐛 Creating new bug report...")
        try:
            if not EnhancedTaskDialog:
                messagebox.showerror("Error", "Enhanced Task Dialog is not available. Please check imports.")
                return

            root_window = self.parent_window.root

            dialog = EnhancedTaskDialog(
                parent=root_window,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=None,
                issue_type="BUG"
            )

            if dialog.result:
                print(f"✅ Bug report created: {dialog.result.title}")
                self._refresh_dashboard_data()

        except Exception as e:
            print(f"❌ Error creating bug: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to create bug: {str(e)}")

    def _new_feature(self):
        """Create new feature request"""
        print("✨ Creating new feature request...")
        try:
            if not EnhancedTaskDialog:
                messagebox.showerror("Error", "Enhanced Task Dialog is not available. Please check imports.")
                return

            root_window = self.parent_window.root

            dialog = EnhancedTaskDialog(
                parent=root_window,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=None,
                issue_type="FEATURE"
            )

            if dialog.result:
                print(f"✅ Feature request created: {dialog.result.title}")
                self._refresh_dashboard_data()

        except Exception as e:
            print(f"❌ Error creating feature: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to create feature: {str(e)}")

    def _view_task_details(self, task: Task):
        """View task details"""
        print(f"👁️ Viewing task details: {task.title}")
        try:
            if not EnhancedTaskDialog:
                messagebox.showerror("Error", "Enhanced Task Dialog is not available. Please check imports.")
                return

            root_window = self.parent_window.root

            dialog = EnhancedTaskDialog(
                parent=root_window,
                task_controller=self.task_controller,
                project_controller=self.project_controller,
                task=task,
                issue_type=None
            )

            if dialog.result:
                print(f"✅ Task updated: {dialog.result.title}")
                self._refresh_dashboard_data()

        except Exception as e:
            print(f"❌ Error viewing task: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to view task: {str(e)}")

    def _apply_quick_filter(self, filter_criteria: dict):
        """POPRAWIONA METODA - Apply quick filter and refresh dashboard"""
        print(f"🔍 Applying dashboard quick filter: {filter_criteria}")

        try:
            # Utwórz nowy filtr
            new_filter = SearchFilter()

            # Zastosuj kryteria filtra
            if 'issue_type' in filter_criteria:
                new_filter.issue_type = filter_criteria['issue_type']

            elif 'priority' in filter_criteria:
                new_filter.priority = filter_criteria['priority']

            elif 'module_name' in filter_criteria:
                # Znajdź ID modułu po nazwie
                try:
                    modules = self.db_manager.get_all_modules()
                    module = next((m for m in modules if m.name == filter_criteria['module_name']), None)
                    if module:
                        new_filter.module_id = module.id
                    else:
                        print(f"⚠️ Module {filter_criteria['module_name']} not found")
                except Exception as e:
                    print(f"⚠️ Error finding module: {e}")

            elif 'assignee_id' in filter_criteria:
                new_filter.assignee_id = filter_criteria['assignee_id']

            elif 'status_open' in filter_criteria:
                # Dla otwartych zadań - nie ustawiamy konkretnego statusu
                # To będzie obsłużone w logice wyszukiwania
                pass

            # Aktualizuj filtr i odśwież dashboard
            self.update_filter(new_filter)

            # NOWE - poinformuj główne okno o zmianie filtra (jeśli to potrzebne)
            if hasattr(self.parent_window, '_apply_filter'):
                self.parent_window.current_filter = new_filter

        except Exception as e:
            print(f"❌ Error applying filter: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Filter Error", f"Failed to apply filter: {str(e)}")

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color for hover effect"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def __del__(self):
        """Destructor - clean up event handlers"""
        try:
            self._cleanup_event_handlers()
        except:
            pass