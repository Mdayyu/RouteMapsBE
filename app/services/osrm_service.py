import requests

OSRM_URL = "http://router.project-osrm.org"

def get_osrm_route(coord1, coord2, vehicle="car"):
    # OSRM menggunakan format lon,lat
    coords = f"{coord1[1]},{coord1[0]};{coord2[1]},{coord2[0]}"
    url = f"{OSRM_URL}/route/v1/driving/{coords}?overview=full&geometries=geojson"

    response = requests.get(url)
    data = response.json()

    route = data["routes"][0]

    # Konversi ke km & menit
    distance_km = route["distance"] / 1000
    duration_min = route["duration"] / 60

    # Sesuaikan untuk motor
    if vehicle == "motor":
        duration_min *= 0.85  # motor lebih cepat

    geometry = [
        (lat, lon)
        for lon, lat in route["geometry"]["coordinates"]
    ]

    return distance_km, duration_min, geometry
