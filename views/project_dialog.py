"""
Project creation and editing dialog - SOFT DARK MODE ✨
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from controllers.project_controller import ProjectController
from models.entities import Project


class ProjectDialog:
    """Dialog for creating and editing projects - Soft Dark Theme"""

    def __init__(self, parent, project_controller: ProjectController,
                 project: Optional[Project] = None):
        self.project_controller = project_controller
        self.project = project
        self.result = None

        # Soft Dark color palette
        self.colors = {
            'bg_primary': '#1A202C',
            'bg_secondary': '#2D3748',
            'bg_card': '#374151',
            'bg_hover': '#4B5563',
            'text_primary': '#F7FAFC',
            'text_secondary': '#CBD5E0',
            'text_muted': '#A0AEC0',
            'blue': '#4299E1',
            'green': '#48BB78',
            'orange': '#ED8936',
            'red': '#F56565',
            'border_light': '#4A5568',
        }

        # Generate project identifier for display (if editing)
        project_id_str = ""
        if project:
            project_prefix = project.name[:3].upper()
            project_id_str = f" (#{project_prefix}{project.id:03d})"

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        if project:
            self.dialog.title(f"Edit Project: {project.name}{project_id_str}")
        else:
            self.dialog.title("New Project")

        self.dialog.geometry("500x400")
        self.dialog.configure(bg=self.colors['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._load_data()

        # Wait for dialog to close
        self.dialog.wait_window()

    def _create_widgets(self):
        """Create dialog widgets with soft dark styling"""

        # Main frame with dark background
        main_frame = tk.Frame(self.dialog, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_label = tk.Label(main_frame,
                                text="📁 Project Details" if self.project else "📁 New Project",
                                bg=self.colors['bg_primary'],
                                fg=self.colors['text_primary'],
                                font=('Segoe UI', 14, 'bold'))
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Name field
        tk.Label(main_frame, text="Name:",
                 bg=self.colors['bg_primary'],
                 fg=self.colors['text_primary'],
                 font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=(0, 5))

        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(main_frame,
                                   textvariable=self.name_var,
                                   width=40,
                                   bg=self.colors['bg_card'],
                                   fg=self.colors['text_primary'],
                                   insertbackground=self.colors['blue'],
                                   relief='flat',
                                   bd=8,
                                   font=('Segoe UI', 10))
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=(0, 15))
        self.name_entry.focus()

        # Description field
        tk.Label(main_frame, text="Description:",
                 bg=self.colors['bg_primary'],
                 fg=self.colors['text_primary'],
                 font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky="nw", pady=(0, 5))

        # Description text area with dark styling
        desc_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        desc_frame.grid(row=2, column=1, sticky="nsew", pady=(0, 20))

        self.description_text = tk.Text(desc_frame,
                                        height=10,
                                        width=40,
                                        wrap=tk.WORD,
                                        bg=self.colors['bg_card'],
                                        fg=self.colors['text_primary'],
                                        insertbackground=self.colors['blue'],
                                        relief='flat',
                                        bd=8,
                                        font=('Segoe UI', 10))

        scrollbar = tk.Scrollbar(desc_frame,
                                 orient=tk.VERTICAL,
                                 command=self.description_text.yview,
                                 bg=self.colors['bg_secondary'],
                                 troughcolor=self.colors['bg_card'],
                                 activebackground=self.colors['blue'])
        self.description_text.configure(yscrollcommand=scrollbar.set)

        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons section
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        # Cancel button
        cancel_btn = tk.Label(button_frame,
                              text="Cancel",
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_secondary'],
                              font=('Segoe UI', 10),
                              padx=20,
                              pady=10,
                              cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Save button
        save_btn = tk.Label(button_frame,
                            text="Save Project",
                            bg=self.colors['blue'],
                            fg=self.colors['text_primary'],
                            font=('Segoe UI', 10, 'bold'),
                            padx=20,
                            pady=10,
                            cursor='hand2')
        save_btn.pack(side=tk.RIGHT)

        # Button hover effects
        def on_cancel_enter(e):
            cancel_btn.configure(bg=self.colors['bg_hover'])
        def on_cancel_leave(e):
            cancel_btn.configure(bg=self.colors['bg_secondary'])
        def on_cancel_click(e):
            self._cancel()

        def on_save_enter(e):
            save_btn.configure(bg=self.colors['green'])
        def on_save_leave(e):
            save_btn.configure(bg=self.colors['blue'])
        def on_save_click(e):
            self._save_project()

        cancel_btn.bind("<Enter>", on_cancel_enter)
        cancel_btn.bind("<Leave>", on_cancel_leave)
        cancel_btn.bind("<Button-1>", on_cancel_click)

        save_btn.bind("<Enter>", on_save_enter)
        save_btn.bind("<Leave>", on_save_leave)
        save_btn.bind("<Button-1>", on_save_click)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def _load_data(self):
        """Load data into form"""
        if self.project:
            self.name_var.set(self.project.name)
            if self.project.description:
                self.description_text.insert(1.0, self.project.description)

    def _save_project(self):
        """Save project with validation"""
        # Validate inputs
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Name is required")
            return

        try:
            # Create or update project
            project_data = Project(
                id=self.project.id if self.project else None,
                name=self.name_var.get().strip(),
                description=self.description_text.get(1.0, tk.END).strip() or None
            )

            if self.project:
                # Update existing project
                self.project_controller.update_project(project_data)
                project_prefix = self.project.name[:3].upper()
                project_id_str = f"{project_prefix}{self.project.id:03d}"
                print(f"✅ Project updated: {project_data.name} (#{project_id_str})")
            else:
                # Create new project
                new_project_id = self.project_controller.create_project(project_data)
                project_prefix = project_data.name[:3].upper()
                project_id_str = f"{project_prefix}{new_project_id:03d}"
                print(f"✅ Project created: {project_data.name} (#{project_id_str})")

            self.result = project_data
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {str(e)}")

    def _cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()