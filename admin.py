import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database as db

class AssignDriverDialog(simpledialog.Dialog):
    def __init__(self, parent, ride_id):
        self.ride_id = ride_id
        super().__init__(parent, title=f"Assign driver to ride {ride_id}")

    def body(self, master):
        ttk.Label(master, text="Select Driver:").grid(row=0, column=0, sticky="w")
        self.driver_var = tk.StringVar()
        self.drivers = db.list_users(role="driver")
        # prepare list entries as "id - username (phone)"
        options = []
        for d in self.drivers:
            options.append(f"{d['id']} - {d['username']} ({d.get('phone') or '-'})")
        self.combo = ttk.Combobox(master, values=options, state="readonly", width=40, textvariable=self.driver_var)
        self.combo.grid(row=1, column=0, padx=6, pady=6)
        return self.combo

    def validate(self):
        if not self.driver_var.get():
            messagebox.showwarning("Select", "Select a driver")
            return False
        return True

    def apply(self):
        sel = self.driver_var.get()
        # parse id from "id - username ..."
        driver_id = int(sel.split(" - ", 1)[0].strip())
        ok, err = db.assign_driver_to_ride(self.ride_id, driver_id)
        if not ok:
            messagebox.showerror("Could not assign", err or "Unknown error")
            self.result = False
        else:
            messagebox.showinfo("Assigned", f"Ride {self.ride_id} assigned to driver id {driver_id}")
            self.result = True

class AdminPage(ttk.Frame):
    def __init__(self, parent, user, master_app):
        super().__init__(parent)
        self.user = user
        self.master_app = master_app
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_users()
        self.refresh_rides()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=6)
        ttk.Label(top, text=f"Admin: {self.user['username']}", font=("Segoe UI", 14, "bold")).pack(side="left", padx=10)
        ttk.Button(top, text="Logout", command=self.master_app.logout).pack(side="right", padx=10)

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=6)

        users_frame = ttk.Labelframe(paned, text="Users", padding=6, width=350)
        paned.add(users_frame, weight=1)
        self.users_tree = ttk.Treeview(users_frame, columns=("id","username","email","phone","role"), show="headings")
        for c,h in [("id","ID"),("username","Username"),("email","Email"),("phone","Phone"),("role","Role")]:
            self.users_tree.heading(c, text=h)
            self.users_tree.column(c, width=100, anchor="center")
        self.users_tree.pack(fill="both", expand=True)
        btns = ttk.Frame(users_frame); btns.pack(pady=6)
        ttk.Button(btns, text="Delete", command=self.delete_user).pack(side="left", padx=4)
        ttk.Button(btns, text="Refresh", command=self.refresh_users).pack(side="left", padx=4)

        rides_frame = ttk.Labelframe(paned, text="Rides", padding=6)
        paned.add(rides_frame, weight=2)
        self.rides_tree = ttk.Treeview(rides_frame, columns=("id","customer","phone","driver","pickup",
                                                             "dropoff","date","time","fare","status"), show="headings")
        for c,h in [("id","ID"),("customer","Customer"),("phone","Cust Phone"),("driver","Driver"),("pickup","Pickup"),
                    ("dropoff","Dropoff"),("date","Date"),("time","Time"),("fare","Fare"),("status","Status")]:
            self.rides_tree.heading(c, text=h)
            self.rides_tree.column(c, width=100, anchor="center")
        self.rides_tree.pack(fill="both", expand=True)
        btns2 = ttk.Frame(rides_frame); btns2.pack(pady=6)
        ttk.Button(btns2, text="Assign Driver", command=self.assign_driver_to_selected).pack(side="left", padx=4)
        ttk.Button(btns2, text="Refresh", command=self.refresh_rides).pack(side="left", padx=4)

    def refresh_users(self):
        for i in self.users_tree.get_children():
            self.users_tree.delete(i)
        rows = db.list_users()
        for u in rows:
            self.users_tree.insert("", "end", values=(u["id"], u["username"], u.get("email") or "-", u.get("phone") or 
                                                      "-", u["role"]))

    def delete_user(self):
        sel = self.users_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a user")
            return
        uid = self.users_tree.item(sel[0], "values")[0]
        if messagebox.askyesno("Confirm", "Delete selected user?"):
            db.delete_user(uid)
            self.refresh_users()
            messagebox.showinfo("Deleted", "User removed.")

    def refresh_rides(self):
        for i in self.rides_tree.get_children():
            self.rides_tree.delete(i)
        rows = db.list_all_rides()
        for r in rows:
            self.rides_tree.insert("", "end", values=(
                r["id"],
                r.get("customer_name") or "-",
                r.get("customer_phone") or "-",
                r.get("driver_name") or "-",
                r["pickup"],
                r["dropoff"],
                r["date"],
                r["time"],
                r["fare"],
                r["status"]
            ))

    def assign_driver_to_selected(self):
        sel = self.rides_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a ride")
            return
        ride_id = int(self.rides_tree.item(sel[0], "values")[0])
        # open dialog to choose driver
        d = AssignDriverDialog(self, ride_id)
        if getattr(d, "result", False):
            self.refresh_rides()
