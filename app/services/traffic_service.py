import requests

def get_traffic_lights(center, radius=1500):
    """
    Mendapatkan semua lampu lalu lintas dalam radius (meter)
    dari titik awal (LLDIKTI).
    """
    query = f"""
    [out:json];
    node["highway"="traffic_signals"]
      (around:{radius},{center[0]},{center[1]});
    out;
    """
    url = "https://overpass-api.de/api/interpreter"
    response = requests.get(url, params={"data": query})
    data = response.json()

    return [
        (el["lat"], el["lon"])
        for el in data["elements"]
    ]

def count_lights_on_route(route, lights):
    """
    Menghitung lampu di sepanjang route.
    route = list titik (lat,lon)
    lights = list titik lampu
    """
    count = 0
    for light in lights:
        for p in route[::10]:
            if haversine_m(light, p) < 50:
                count += 1
                break
    return count

from app.utils.geo import haversine_m
