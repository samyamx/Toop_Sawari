import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, date 
import database as db
import farecalculation as farecalc
import map as maps


class CustomerPage(ttk.Frame):
    def __init__(self, parent, user, master_app):
        super().__init__(parent)
        self.user = user
        self.master_app = master_app
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_history()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=6)
        ttk.Label(
            top,
            text=f"Welcome, {self.user['username']}",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=10)
        ttk.Button(
            top,
            text="Logout",
            command=self.master_app.logout
        ).pack(side="right", padx=10)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=6)

        # -------- New Ride --------
        newride = ttk.Labelframe(body, text="Book New Ride", width=350, padding=10)
        body.add(newride, weight=1)

        ttk.Label(newride, text="Pickup (address or lat,lon)").grid(row=0, column=0, sticky="w")
        self.pickup = ttk.Entry(newride, width=40)
        self.pickup.grid(row=1, column=0, pady=4)

        ttk.Label(newride, text="Dropoff (address or lat,lon)").grid(row=2, column=0, sticky="w")
        self.dropoff = ttk.Entry(newride, width=40)
        self.dropoff.grid(row=3, column=0, pady=4)

        ttk.Label(newride, text="Date (YYYY-MM-DD)").grid(row=4, column=0, sticky="w")
        self.date = ttk.Entry(newride, width=20)
        self.date.grid(row=5, column=0, pady=4)

        ttk.Label(newride, text="Time (HH:MM)").grid(row=6, column=0, sticky="w")
        self.time = ttk.Entry(newride, width=20)
        self.time.grid(row=7, column=0, pady=4)

        ttk.Button(
            newride,
            text="Estimate Fare",
            command=self.start_fare_thread
        ).grid(row=8, column=0, pady=6)

        self.fare_var = tk.StringVar(value="Fare: -")
        ttk.Label(
            newride,
            textvariable=self.fare_var,
            font=("Segoe UI", 11, "bold")
        ).grid(row=9, column=0, pady=4)

        ttk.Button(
            newride,
            text="Book Ride",
            command=self.book_ride
        ).grid(row=10, column=0, pady=8)

        # -------- Ride History --------
        history = ttk.Labelframe(body, text="My Rides", padding=6)
        body.add(history, weight=2)

        cols = ("id", "pickup", "dropoff", "date", "time", "fare", "status", "driver")
        self.tree = ttk.Treeview(history, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

        ttk.Button(
            self,
            text="Open Map for selected ride",
            command=self.open_map_for_selected
        ).pack(pady=6)

    # -------- NON-BLOCKING FARE CALCULATION --------
    def start_fare_thread(self):
        p = self.pickup.get().strip()
        d = self.dropoff.get().strip()

        if not p or not d:
            messagebox.showwarning("Missing", "Provide both pickup and dropoff")
            return

        self.fare_var.set("Calculating... Please wait...")

        thread = threading.Thread(
            target=self.calculate_fare_thread,
            args=(p, d)
        )
        thread.daemon = True
        thread.start()

    def calculate_fare_thread(self, pickup, dropoff):
        try:
            fare, dist, provider = farecalc.calculate_fare(pickup, dropoff)
            result = f"Fare: NPR {fare}  (est. {dist} km via {provider})"
        except Exception as e:
            result = f"Error calculating fare: {e}"

        self.after(0, lambda: self.fare_var.set(result))

    # -------- BOOK RIDE WITH DATE VALIDATION --------
    def book_ride(self):
        p = self.pickup.get().strip()
        d = self.dropoff.get().strip()
        date_str = self.date.get().strip()
        time = self.time.get().strip()

        if not p or not d or not date_str or not time:
            messagebox.showwarning("Missing", "Fill all fields")
            return

        # ✅ DATE VALIDATION (NO PAST DATE ALLOWED)
        try:
            ride_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = date.today()

            if ride_date < today:
                messagebox.showerror(
                    "Invalid Date",
                    "You cannot book a ride for a past date."
                )
                return
        except ValueError:
            messagebox.showerror(
                "Invalid Date Format",
                "Date must be in YYYY-MM-DD format."
            )
            return

        fare, dist, provider = farecalc.calculate_fare(p, d)
        ride_id = db.add_ride(
            self.user['id'],
            p,
            d,
            date_str,
            time,
            fare
        )

        if ride_id:
            messagebox.showinfo(
                "Booked",
                f"Ride booked (id={ride_id}). Waiting for driver."
            )
            self.refresh_history()
        else:
            messagebox.showerror("Error", "Could not book ride.")

    # -------- REFRESH HISTORY --------
    def refresh_history(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        rows = db.list_rides_for_customer(self.user['id'])
        for r in rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    r["id"],
                    r["pickup"],
                    r["dropoff"],
                    r["date"],
                    r["time"],
                    r["fare"],
                    r["status"],
                    r.get("driver_name") or "-"
                )
            )

    # -------- OPEN MAP --------
    def open_map_for_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a ride")
            return

        vals = self.tree.item(sel[0], "values")
        maps.open_in_map(vals[1], vals[2])
