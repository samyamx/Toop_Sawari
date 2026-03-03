import tkinter as tk
from tkinter import ttk, messagebox
import database as db
import map as maps

class DriverPage(ttk.Frame):
    def __init__(self, parent, user, master_app):
        super().__init__(parent)
        self.user = user
        self.master_app = master_app
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_requests()
        self.refresh_history()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=6)
        ttk.Label(top, text=f"Driver: {self.user['username']}", font=("Segoe UI", 14, "bold")).pack(side="left", padx=10)
        ttk.Button(top, text="Logout", command=self.master_app.logout).pack(side="right", padx=10)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=6)

        requests = ttk.Labelframe(body, text="Ride Requests (pending)", padding=6, width=350)
        body.add(requests, weight=1)
        self.req_tree = ttk.Treeview(requests, columns=("id","customer","phone","pickup","dropoff","date","time","fare"), show="headings")
        for c,h in [("id","ID"),("customer","Customer"),("phone","Phone"),("pickup","Pickup"),("dropoff","Dropoff"),("date","Date"),("time","Time"),("fare","Fare")]:
            self.req_tree.heading(c, text=h)
            self.req_tree.column(c, width=100, anchor="center")
        self.req_tree.pack(fill="both", expand=True)
        btns = ttk.Frame(requests)
        btns.pack(pady=4)
        ttk.Button(btns, text="Accept", command=self.accept_selected).pack(side="left", padx=4)
        ttk.Button(btns, text="Reject", command=self.reject_selected).pack(side="left", padx=4)
        ttk.Button(btns, text="Open Map", command=self.open_map_selected).pack(side="left", padx=4)

        history = ttk.Labelframe(body, text="My History", padding=6)
        body.add(history, weight=2)
        self.h_tree = ttk.Treeview(history, columns=("id","customer","pickup","dropoff","date","time","fare","status"), show="headings")
        for c,h in [("id","ID"),("customer","Customer"),("pickup","Pickup"),("dropoff","Dropoff"),("date","Date"),("time","Time"),("fare","Fare"),("status","Status")]:
            self.h_tree.heading(c, text=h)
            self.h_tree.column(c, width=90, anchor="center")
        self.h_tree.pack(fill="both", expand=True)
        h_btns = ttk.Frame(history); h_btns.pack(pady=6)
        ttk.Button(h_btns, text="Refresh", command=self.refresh_history).pack(side="left", padx=4)
        ttk.Button(h_btns, text="Mark Selected Complete", command=self.complete_selected).pack(side="left", padx=6)

    def refresh_requests(self):
        for i in self.req_tree.get_children():
            self.req_tree.delete(i)
        rows = db.list_requests_for_driver(self.user['id'])
        for r in rows:
            self.req_tree.insert("", "end", values=(
                r["id"],
                r.get("customer_name") or "-",
                r.get("customer_phone") or "-",
                r["pickup"],
                r["dropoff"],
                r["date"],
                r["time"],
                r["fare"]
            ))

    def refresh_history(self):
        for i in self.h_tree.get_children():
            self.h_tree.delete(i)
        all_rides = db.list_all_rides()
        for r in all_rides:
            # r["driver_id"] may be None or int; compare as int
            if r.get("driver_id") == self.user['id']:
                self.h_tree.insert("", "end", values=(
                    r["id"],
                    r.get("customer_name") or "-",
                    r["pickup"],
                    r["dropoff"],
                    r["date"],
                    r["time"],
                    r["fare"],
                    r["status"]
                ))

    def accept_selected(self):
        sel = self.req_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a request")
            return
        rid = int(self.req_tree.item(sel[0], "values")[0])

        # Check driver doesn't already have an active ride
        if db.driver_has_active_ride(self.user['id']):
            messagebox.showwarning("Busy", "You already have an active ride (accepted/ongoing). Complete it before accepting another.")
            return

        ok, err = db.assign_driver_to_ride(rid, self.user['id'])
        if not ok:
            messagebox.showerror("Cannot accept", err or "Unknown error")
            self.refresh_requests()
            return

        messagebox.showinfo("Accepted", f"Ride {rid} accepted.")
        self.refresh_requests()
        self.refresh_history()

    def reject_selected(self):
        sel = self.req_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a request")
            return
        rid = int(self.req_tree.item(sel[0], "values")[0])
        db.reject_ride(rid)
        messagebox.showinfo("Rejected", f"Ride {rid} rejected.")
        self.refresh_requests()

    def open_map_selected(self):
        sel = self.req_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a request")
            return
        vals = self.req_tree.item(sel[0], "values")
        pickup = vals[3]; dropoff = vals[4]
        maps.open_in_map(pickup, dropoff)

    def complete_selected(self):
        sel = self.h_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a ride from history to complete")
            return
        rid = int(self.h_tree.item(sel[0], "values")[0])
        # Only allow completing rides assigned to this driver
        # confirm status
        rows = db.list_all_rides()
        ride = next((r for r in rows if r["id"] == rid), None)
        if not ride:
            messagebox.showerror("Error", "Ride not found")
            return
        if ride.get("driver_id") != self.user['id']:
            messagebox.showerror("Error", "This ride is not assigned to you.")
            return
        if ride.get("status") == "completed":
            messagebox.showinfo("Info", "Ride is already completed.")
            return

        db.mark_ride_completed(rid)
        messagebox.showinfo("Completed", f"Ride {rid} marked as completed.")
        self.refresh_history()
        self.refresh_requests()
