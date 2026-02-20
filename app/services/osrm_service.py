import requests

OSRM_URL = "http://router.project-osrm.org"

def get_osrm_route(coord1, coord2, vehicle="car"):
    # Format koordinat OSRM: lon,lat
    coords = f"{coord1[1]},{coord1[0]};{coord2[1]},{coord2[0]}"

    # ============================
    # Tentukan profile OSRM
    # ============================
    if vehicle == "motor":
        profile = "cycling"   # supaya bisa lewat jalan kecil
    else:
        profile = "driving"

    url = f"{OSRM_URL}/route/v1/{profile}/{coords}?overview=full&geometries=geojson"

    response = requests.get(url)
    data = response.json()

    if "routes" not in data or len(data["routes"]) == 0:
        return 0, 0, []

    route = data["routes"][0]

    # Konversi ke km & menit
    distance_km = route["distance"] / 1000
    duration_min = route["duration"] / 60

    # ============================
    # Penyesuaian Kecepatan Motor
    # ============================
    if vehicle == "motor":
        # Cycling biasanya lebih lambat dari motor,
        # jadi kita percepat agar realistis
        duration_min *= 0.6   # silakan atur 0.5 - 0.7 sesuai kebutuhan

    geometry = [
        (lat, lon)
        for lon, lat in route["geometry"]["coordinates"]
    ]

    return distance_km, duration_min, geometry
