import sqlite3
from datetime import datetime

DB_FILE = "taxi.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        phone TEXT,
        license TEXT,
        role TEXT,
        password TEXT,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        driver_id INTEGER,
        pickup TEXT,
        dropoff TEXT,
        date TEXT,
        time TEXT,
        fare REAL,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY(customer_id) REFERENCES users(id),
        FOREIGN KEY(driver_id) REFERENCES users(id)
    )
    """)
    conn.commit()
    conn.close()

# ---------------- User functions ----------------
def add_user(username, email, phone, license_no, role, password):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username,email,phone,license,role,password,created_at) VALUES (?,?,?,?,?,?,?)",
            (username, email, phone, license_no, role, password, datetime.utcnow().isoformat())
        )
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print("DB add_user error:", e)
        return None
    finally:
        conn.close()

def authenticate(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_username(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def list_users(role=None):
    conn = get_conn()
    cur = conn.cursor()
    if role:
        cur.execute("SELECT * FROM users WHERE role=?", (role,))
    else:
        cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# ---------------- Ride functions ----------------
def add_ride(customer_id, pickup, dropoff, date, time, fare):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""INSERT INTO rides (customer_id, driver_id, pickup, dropoff, date, time, fare, status, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (customer_id, None, pickup, dropoff, date, time, fare, "pending", datetime.utcnow().isoformat()))
    conn.commit()
    ride_id = cur.lastrowid
    conn.close()
    return ride_id

def list_rides_for_customer(customer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT r.*, u.username as driver_name FROM rides r LEFT JOIN users u ON r.driver_id=u.id WHERE r.customer_id=? " \
        "ORDER BY r.created_at DESC",
        (customer_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def list_pending_rides():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, c.username as customer_name, c.phone as customer_phone
        FROM rides r
        LEFT JOIN users c ON r.customer_id=c.id
        WHERE r.status='pending'
        ORDER BY r.created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def list_requests_for_driver(driver_id):
    return list_pending_rides()

def list_all_rides():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, c.username as customer_name, c.phone as customer_phone, d.username as driver_name, d.phone as driver_phone
        FROM rides r
        LEFT JOIN users c ON r.customer_id=c.id
        LEFT JOIN users d ON r.driver_id=d.id
        ORDER BY r.created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def driver_has_active_ride(driver_id):
    """
    Returns True if the driver already has an active ride (accepted or ongoing).
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) as cnt FROM rides WHERE driver_id=? AND status IN ('accepted','ongoing')", (driver_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row["cnt"])

def update_ride_status(ride_id, status, driver_id=None):
    conn = get_conn()
    cur = conn.cursor()
    if driver_id is not None:
        cur.execute("UPDATE rides SET status=?, driver_id=? WHERE id=?", (status, driver_id, ride_id))
    else:
        cur.execute("UPDATE rides SET status=? WHERE id=?", (status, ride_id))
    conn.commit()
    conn.close()

def assign_driver_to_ride(ride_id, driver_id):
    """
    Attempt to assign driver to ride.
    Returns (True, None) on success.
    Returns (False, "reason") on failure.
    """
    # validate ride exists and is pending
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rides WHERE id=?", (ride_id,))
    ride = cur.fetchone()
    if not ride:
        conn.close()
        return False, "Ride not found."

    if ride["status"] != "pending":
        conn.close()
        return False, f"Ride is not pending (current: {ride['status']})."

    # ensure driver exists and is role driver
    cur.execute("SELECT * FROM users WHERE id=? AND role='driver'", (driver_id,))
    drv = cur.fetchone()
    if not drv:
        conn.close()
        return False, "Driver not found."

    # ensure driver has no active ride
    cur.execute("SELECT COUNT(1) as cnt FROM rides WHERE driver_id=? AND status IN ('accepted','ongoing')", (driver_id,))
    row = cur.fetchone()
    if row and row["cnt"] > 0:
        conn.close()
        return False, "Driver already has an active ride."

    # assign: set status to 'accepted' and driver_id
    cur.execute("UPDATE rides SET status='accepted', driver_id=? WHERE id=?", (driver_id, ride_id))
    conn.commit()
    conn.close()
    return True, None

def reject_ride(ride_id):
    update_ride_status(ride_id, "rejected")

def mark_ride_ongoing(ride_id):
    update_ride_status(ride_id, "ongoing")

def mark_ride_completed(ride_id):
    update_ride_status(ride_id, "completed")


if __name__ == "__main__":
    init_db()
    # create a default admin if not exists
    if not get_user_by_username("admin"):
        add_user("admin", "admin@example.com", None, None, "admin", "admin123")
    print("DB initialized")
