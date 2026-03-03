import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import database as db
from register import RegisterWindow
import assets

class LoginWindow(ttk.Frame):
    def __init__(self, parent, master_app):
        super().__init__(parent)
        self.master_app = master_app
        self.parent = parent
        self.pack(fill="both", expand=True)

        # BACKGROUND IMAGE SETTINGS
        self.bg_path = "backgrounds/otaxi.png"   
        self.bg_img = None
        self.bg_label = None

        # Setup theme
        assets.theme_setup(self.winfo_toplevel())

        # Create background
        self.create_background()

        # Create widgets
        self.create_widgets()

        # Resize background when window size changes
        self.bind("<Configure>", self.resize_bg)

    # CREATE BACKGROUND IMAGE
    def create_background(self):
        if not os.path.exists(self.bg_path):
            print("Background image not found:", self.bg_path)
            return

        img = Image.open(self.bg_path)
        self.bg_img = ImageTk.PhotoImage(img)

        self.bg_label = tk.Label(self, image=self.bg_img)
        self.bg_label.place(relwidth=1, relheight=1)

    # Resize background automatically
    def resize_bg(self, event):
        if not os.path.exists(self.bg_path):
            return
        
        img = Image.open(self.bg_path)
        img = img.resize((event.width, event.height))
        self.bg_img = ImageTk.PhotoImage(img)
        self.bg_label.configure(image=self.bg_img)

    # LOGIN UI WIDGETS
    def create_widgets(self):
        container = ttk.Frame(self, padding=20)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo (optional)
        logo = assets.load_icon("logo", size=(64,64))
        if logo:
            ttk.Label(container, image=logo).grid(row=0, column=0, columnspan=2, 
                                                  pady=(0,6))
            self.logo_img = logo

        title = ttk.Label(container, text="ToopSawari", style="Header.TLabel")
        title.grid(row=1, column=0, columnspan=2, pady=(0,12))

        ttk.Label(container, text="Username").grid(row=2, column=0, sticky="e", padx=5, 
                                                   pady=5)
        self.username = ttk.Entry(container, width=30)
        self.username.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(container, text="Password").grid(row=3, column=0, sticky="e", padx=5, 
                                                   pady=5)
        self.password = ttk.Entry(container, width=30, show="*")
        self.password.grid(row=3, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        login_btn = ttk.Button(btn_frame, text="Login", command=self.do_login, 
                               style="Accent.TButton")
        login_btn.grid(row=0, column=0, padx=5)

        register_btn = ttk.Button(btn_frame, text="Register", command=self.open_register)
        register_btn.grid(row=0, column=1, padx=5)

    def open_register(self):
        RegisterWindow(self.parent)

    def do_login(self):
        uname = self.username.get().strip()
        pwd = self.password.get().strip()

        if not uname or not pwd:
            messagebox.showwarning("Missing", "Please provide username and password.")
            return

        user = db.authenticate(uname, pwd)
        if not user:
            messagebox.showerror("Login failed", "Invalid credentials.")
            return

        self.master_app.on_login_success(user)
