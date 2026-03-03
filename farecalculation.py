import math

BASE_FARE = 50.0
PER_KM = 12.0

def _try_parse_latlon(text):
    try:
        parts = [p.strip() for p in text.split(",")]
        if len(parts) == 2:
            return (float(parts[0]), float(parts[1]))
    except:
        return None
    return None

def haversine_km(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    R = 6371.0
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    d = 2 * R * math.asin(math.sqrt(h))
    return max(0.1, d)

def estimate_distance_km(pickup, dropoff):
    a = _try_parse_latlon(pickup)
    b = _try_parse_latlon(dropoff)

    if a and b:
        return haversine_km(a, b), "offline-haversine"

    diff = abs(len(pickup or "") - len(dropoff or ""))
    est = max(1.0, (diff / 3.0) + 2.0)
    return round(est, 2), "offline-estimate"

def calculate_fare(pickup, dropoff):
    distance, provider = estimate_distance_km(pickup, dropoff)
    fare = BASE_FARE + PER_KM * distance
    return round(fare, 2), round(distance, 2), provider
