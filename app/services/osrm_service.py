import requests

OSRM_URL = "http://router.project-osrm.org"

def get_osrm_route(coord1, coord2, vehicle="mobil", debug=False):
    coords = f"{coord1[1]},{coord1[0]};{coord2[1]},{coord2[0]}"

    # ============================
    # PROFILE BERDASARKAN KENDARAAN
    # ============================
    if vehicle == "sepeda":
        profile = "cycling"
        speed_kmh = 15
    else:
        profile = "driving"
        speed_kmh = 40

    url = f"{OSRM_URL}/route/v1/{profile}/{coords}?overview=full&geometries=geojson"

    response = requests.get(url)

    if response.status_code != 200:
        return 0, 0, []

    data = response.json()

    if "routes" not in data or len(data["routes"]) == 0:
        return 0, 0, []

    route = data["routes"][0]

    # Ambil jarak sesuai profile
    distance_km = route["distance"] / 1000

    # Hitung durasi berdasarkan kecepatan rata-rata
    duration_min = (distance_km / speed_kmh) * 60

    geometry = [
        (lat, lon)
        for lon, lat in route["geometry"]["coordinates"]
    ]

    if debug:
        print("Vehicle:", vehicle)
        print("Profile:", profile)
        print("Distance:", round(distance_km, 2))
        print("Speed:", speed_kmh)
        print("Duration:", round(duration_min, 2))

    return distance_km, duration_min, geometry