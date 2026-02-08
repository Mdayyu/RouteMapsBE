from app.data.locations import LOCATIONS
from app.services.osrm_service import get_osrm_route
from app.services.traffic_service import (
    get_traffic_lights,
    count_lights_on_route,
)
from app.config import (
    DISTANCE_WEIGHT,
    TRAFFIC_WEIGHT,
    TRAFFIC_LIGHT_DELAY,
)

def run_aco(data: dict):
    start = "LLDIKTI"
    chosen = data.get("campuses", [])
    vehicle = data.get("vehicle", "car")
    return_to_start = data.get("return_to_start", False)

    # Kalau ingin kembali ke titik awal
    if return_to_start and chosen:
        chosen = chosen + [start]

    # Dapatkan semua lampu merah di sekitar titik
    traffic_lights = get_traffic_lights(LOCATIONS[start], radius=2000)

    current = start
    segments = []
    total_cost = 0
    total_distance = 0
    total_duration = 0

    for campus in chosen:
        dist, dur, route = get_osrm_route(
            LOCATIONS[current],
            LOCATIONS[campus],
            vehicle,
        )

        lights = count_lights_on_route(route, traffic_lights)

        # cost = 70% waktu + 30% jarak
        traffic_delay = lights * TRAFFIC_LIGHT_DELAY
        cost = (
            (DISTANCE_WEIGHT * dist)
            + (TRAFFIC_WEIGHT * traffic_delay)
        )

        segments.append({
            "from": current,
            "to": campus,
            "distance_km": round(dist, 2),
            "duration_min": round(dur, 2),
            "traffic_lights": lights,
            "traffic_delay_min": round(traffic_delay, 1),
            "cost": round(cost, 2),
            "route": route,
        })

        total_cost += cost
        total_distance += dist
        total_duration += (dur + traffic_delay)
        current = campus

    return {
        "total_distance_km": round(total_distance, 2),
        "total_duration_min": round(total_duration, 2),
        "total_cost": round(total_cost, 2),
        "segments": segments,
    }
