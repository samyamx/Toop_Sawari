import webbrowser
import urllib.parse

def open_in_map(pickup, dropoff):
    """
    Open Google Maps directions in the default browser using pickup/dropoff text.
    """
    q = f"https://www.google.com/maps/dir/{urllib.parse.quote(pickup)}/{urllib.parse.quote(dropoff)}"
    webbrowser.open(q)
