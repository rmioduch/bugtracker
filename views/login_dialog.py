"""
Login Dialog - ULTRA SIMPLE VERSION - no wait_window!
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from controllers.user_controller import UserController
from models.entities import User


class LoginDialog:
    """Ultra simple login dialog without wait_window"""

    def __init__(self, parent, user_controller: UserController):
        print("🔐 Creating ULTRA SIMPLE LoginDialog (no wait_window)...")

        self.user_controller = user_controller
        self.authenticated_user: Optional[User] = None
        self.parent = parent
        self.dialog = None

        # Create and show dialog
        self._create_dialog()

        print("✅ Dialog setup completed")

    def _create_dialog(self):
        """Create the dialog window"""
        # Create dialog
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("TaskMaster Login")
        self.dialog.geometry("300x250")
        self.dialog.configure(bg='#2d3748')
        self.dialog.resizable(False, False)

        # Make it appear on top
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 150
        y = (self.dialog.winfo_screenheight() // 2) - 125
        self.dialog.geometry(f"+{x}+{y}")

        # Create widgets
        self._create_widgets()

        # Focus
        self.username_entry.focus_set()

        print("✅ Dialog window created and shown")

    def _create_widgets(self):
        """Create dialog widgets"""
        # Main container
        main_frame = tk.Frame(self.dialog, bg='#2d3748')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame,
                               text="TaskMaster Login",
                               bg='#2d3748', fg='white',
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))

        # Username field
        tk.Label(main_frame, text="Username:",
                 bg='#2d3748', fg='white',
                 font=('Arial', 10)).pack(anchor='w', pady=(0, 2))

        self.username_var = tk.StringVar(value="admin")
        self.username_entry = tk.Entry(main_frame,
                                       textvariable=self.username_var,
                                       font=('Arial', 10),
                                       width=25)
        self.username_entry.pack(pady=(0, 10))

        # Password field
        tk.Label(main_frame, text="Password:",
                 bg='#2d3748', fg='white',
                 font=('Arial', 10)).pack(anchor='w', pady=(0, 2))

        self.password_var = tk.StringVar(value="admin123")
        self.password_entry = tk.Entry(main_frame,
                                       textvariable=self.password_var,
                                       show="*",
                                       font=('Arial', 10),
                                       width=25)
        self.password_entry.pack(pady=(0, 15))

        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg='#2d3748')
        btn_frame.pack(fill=tk.X)

        # Login button
        login_btn = tk.Button(btn_frame,
                              text="Login",
                              command=self._on_login_click,
                              bg='#4CAF50',
                              fg='white',
                              font=('Arial', 10, 'bold'),
                              width=10)
        login_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Cancel button
        cancel_btn = tk.Button(btn_frame,
                               text="Cancel",
                               command=self._on_cancel_click,
                               bg='#f44336',
                               fg='white',
                               font=('Arial', 10),
                               width=10)
        cancel_btn.pack(side=tk.RIGHT)

        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self._on_login_click())

        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel_click)

    def _on_login_click(self):
        """Handle login button click"""
        username = self.username_var.get().strip()
        password = self.password_var.get()

        print(f"🔐 Login clicked: username='{username}'")

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return

        try:
            # Authenticate
            success, user, message = self.user_controller.authenticate_user(username, password)

            if success:
                print(f"✅ Authentication successful: {user.full_name}")
                self.authenticated_user = user

                # Close dialog immediately - NO messagebox!
                self._close_dialog()

            else:
                print(f"❌ Authentication failed: {message}")
                messagebox.showerror("Login Failed", message)

                # Clear password and refocus
                self.password_var.set("")
                self.password_entry.focus_set()

        except Exception as e:
            print(f"❌ Login error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Login failed: {str(e)}")

    def _on_cancel_click(self):
        """Handle cancel button click"""
        print("❌ Login cancelled by user")
        self.authenticated_user = None
        self._close_dialog()

    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            try:
                self.dialog.destroy()
                print("✅ Login dialog closed")
            except:
                pass


# Simple test to check if dialog works
if __name__ == "__main__":
    print("🧪 Testing ultra simple login dialog...")

    # Create test root
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("400x300")

    def test_login():
        try:
            from controllers.user_controller import UserController
            user_controller = UserController()

            dialog = LoginDialog(root, user_controller)

            # Check result after some time
            def check_result():
                if dialog.authenticated_user:
                    print(f"✅ Test success: {dialog.authenticated_user.full_name}")
                else:
                    print("❌ Test failed: No user authenticated")
                root.after(1000, root.quit)  # Close after 1 second

            root.after(5000, check_result)  # Check after 5 seconds

        except Exception as e:
            print(f"❌ Test error: {e}")
            import traceback
            traceback.print_exc()

    # Test button
    test_btn = tk.Button(root, text="Test Login Dialog", command=test_login)
    test_btn.pack(pady=50)

    root.mainloop()
    print("🧪 Test completed")