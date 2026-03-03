import tkinter as tk
from tkinter import ttk
import database as db
from login import LoginWindow
from customer import CustomerPage
from driver import DriverPage
from admin import AdminPage
import assets

class App:
    def __init__(self, root):
        self.root = root
        root.title("ToopSawari")
        root.geometry("980x640")
        # Setup theme / accent
        assets.theme_setup(root, accent="#0a79f8")
        self.current_frame = None
        db.init_db()
        if not db.get_user_by_username("admin"):
            db.add_user("admin","admin@gmail.com",None,None,"admin","123")
        self.show_login()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = None

    def show_login(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)
        LoginWindow(self.current_frame, self)

    def on_login_success(self, user):
        role = user["role"]
        self.clear_frame()
        if role == "customer":
            self.current_frame = CustomerPage(self.root, user, self)
        elif role == "driver":
            self.current_frame = DriverPage(self.root, user, self)
        elif role == "admin":
            self.current_frame = AdminPage(self.root, user, self)
        else:
            tk.messagebox.showerror("Error", "Unknown role")
            self.show_login()

    def logout(self):
        self.show_login()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()















