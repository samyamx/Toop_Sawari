import tkinter as tk
from tkinter import ttk, messagebox
import database as db

class RegisterWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register")
        self.geometry("420x420")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        # Role selection
        ttk.Label(self, text="Select role").pack(pady=8)
        self.role = tk.StringVar(value="customer")
        roles = ttk.Frame(self)
        roles.pack()
        for r in ("customer", "driver", "admin"):
            ttk.Radiobutton(
                roles, text=r.capitalize(), variable=self.role, value=r, 
                command=self.build_form
            ).pack(side="left", padx=6)

        # Form container
        self.form = ttk.Frame(self, padding=10)
        self.form.pack(fill="both", expand=True)
        self.build_form()

    def clear_form(self):
        for w in self.form.winfo_children():
            w.destroy()

    def build_form(self):
        self.clear_form()
        role = self.role.get()
        row = 0

        ttk.Label(
            self.form, text=f"Register as {role.capitalize()}", 
            font=("Segoe UI", 12, "bold")
        ).grid(row=row, column=0, columnspan=2, pady=6)
        row += 1

        # Username
        ttk.Label(self.form, text="Username").grid(row=row, column=0, sticky="e")
        self.username = ttk.Entry(self.form)
        self.username.grid(row=row, column=1, pady=4)
        row += 1

        # Email
        ttk.Label(self.form, text="Email").grid(row=row, column=0, sticky="e")
        self.email = ttk.Entry(self.form)
        self.email.grid(row=row, column=1, pady=4)
        row += 1

        # Phone (for all roles)
        if role in ("customer", "driver", "admin"):
            ttk.Label(self.form, text="Phone").grid(row=row, column=0, sticky="e")
            self.phone = ttk.Entry(self.form)
            self.phone.grid(row=row, column=1, pady=4)
            row += 1

        # Driver license
        if role == "driver":
            ttk.Label(self.form, text="License No").grid(row=row, column=0, sticky="e")
            self.license = ttk.Entry(self.form)
            self.license.grid(row=row, column=1, pady=4)
            row += 1

        # Password
        ttk.Label(self.form, text="Password").grid(row=row, column=0, sticky="e")
        self.password = ttk.Entry(self.form, show="*")
        self.password.grid(row=row, column=1, pady=4)
        row += 1

        # Register button
        ttk.Button(self.form, text="Register", command=self.do_register).grid(
            row=row, column=0, columnspan=2, pady=12
        )

    def do_register(self):
        role = self.role.get()
        username = self.username.get().strip()
        email = self.email.get().strip()
        password = self.password.get().strip()
        phone = getattr(self, "phone", None)
        phone = phone.get().strip() if phone else None
        license_no = getattr(self, "license", None)
        license_no = license_no.get().strip() if license_no else None

        # ------------------------
        # Validation
        # ------------------------
        if not username or not email or not password:
            messagebox.showwarning("Missing", "Please fill required fields.")
            return
        
        # Basic email format check (only one @)
        if email.count("@") != 1:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return

        # Phone validation: only digits
        if phone and not phone.isdigit():
            messagebox.showwarning("Invalid Phone", "Phone number must contain only digits.")
            return

        # ------------------------
        # Register user
        # ------------------------
        uid = db.add_user(username, email, phone, license_no, role, password)
        if uid:
            messagebox.showinfo("Success", f"{role.capitalize()} registered. You can now login.")
            self.destroy()
        else:
            messagebox.showerror(
                "Error", "Could not register (username or email may already exist)."
            )
