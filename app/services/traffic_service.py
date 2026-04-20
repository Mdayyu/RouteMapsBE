import requests

def get_traffic_lights(center, radius=1500):
    """
    Mendapatkan semua lampu lalu lintas dalam radius (meter)
    dari titik awal menggunakan Overpass API.
    """

    query = f"""
    [out:json][timeout:25];
    node["highway"="traffic_signals"]
      (around:{radius},{center[0]},{center[1]});
    out;
    """

    # server Overpass alternatif (lebih stabil)
    url = "https://overpass.kumi.systems/api/interpreter"

    try:
        response = requests.get(url, params={"data": query}, timeout=30)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        print("Request error:", e)
        return []

    except ValueError as e:
        print("JSON decode error:", e)
        print("Response text:", response.text[:200])
        return []

    lights = [
        (el["lat"], el["lon"])
        for el in data.get("elements", [])
        if "lat" in el and "lon" in el
    ]

    print("Traffic lights found:", len(lights))  # debug

    return lights

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
