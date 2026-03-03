import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

ICON_SIZE = (40, 40)

_loaded_icons = {}

def load_icon(name, size=ICON_SIZE):
    path = os.path.join("icons", f"{name}.png")
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        img = img.resize(size, Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        _loaded_icons[name] = photo
        return photo
    except Exception as e:
        print("icon load error:", e)
        return None

def theme_setup(root, accent="#2a9df4", font_family="Segoe UI"):
    style = ttk.Style(root)
    default_font = (font_family, 10)
    heading_font = (font_family, 14, "bold")
    style.configure(".", font=default_font)
    style.configure("TLabel", padding=4)
    style.configure("TButton", padding=6)
    style.configure("Header.TLabel", font=heading_font)
    style.configure("Accent.TButton", foreground="white")
    style.configure("Card.TFrame", background="#f1eeee", relief="flat")
    try:
        style.theme_use("clam")
    except:
        pass
    root.accent_color = accent
