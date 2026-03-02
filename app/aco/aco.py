import numpy as np
import random
import pandas as pd
import os

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
# load dataset
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(BASE_DIR, "data", "Locations_Yogyakarta.xlsx")

df = pd.read_excel(file_path)

# Ubah koma jadi titik lalu convert ke float
df["Latitude"] = df["Latitude"].astype(str).str.replace(",", ".").astype(float)
df["Longitude"] = df["Longitude"].astype(str).str.replace(",", ".").astype(float)

LOCATIONS = {
    row["Name"]: (row["Latitude"], row["Longitude"])
    for _, row in df.iterrows()
}

def run_aco(data: dict):
    start = "LLDIKTI"
    chosen = data.get("campuses", [])
    vehicle = data.get("vehicle", "mobil")
    return_to_start = data.get("returnToStart", False)

    if not chosen:
        return {}

    # ==============================
    # PARAMETER ACO
    # ==============================
    ALPHA = 1
    BETA = 2
    EVAPORATION = 0.5
    Q = 100
    NUM_ANTS = 10
    NUM_ITERATIONS = 10

    nodes = [start] + chosen
    n = len(nodes)

    traffic_lights = get_traffic_lights(LOCATIONS[start], radius=2000)

    # ==============================
    # 4.1.2 COST MATRIX + VISIBILITY
    # ==============================
    cost_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                dist, dur, route = get_osrm_route(
                    LOCATIONS[nodes[i]],
                    LOCATIONS[nodes[j]],
                    vehicle,
                )

                lights = count_lights_on_route(route, traffic_lights)
                traffic_delay = lights * TRAFFIC_LIGHT_DELAY
                total_time = dur + traffic_delay  # waktu total = durasi + delay lampu 

                #perhitungan cost
                cost = (
                    (DISTANCE_WEIGHT * dist)
                    + (TRAFFIC_WEIGHT * (dur + traffic_delay))
                )


                cost_matrix[i][j] = cost
            else:
                cost_matrix[i][j] = np.inf

    #perhitungan visibilitas
    visibility = 1 / cost_matrix

    # ==============================
    #  INIT PHEROMONE
    # ==============================
    pheromone = np.ones((n, n))

    best_route = None
    best_cost = float("inf")

    # ==============================
    # ITERATION ACO
    # ==============================
    for _ in range(NUM_ITERATIONS):

        delta_pheromone = np.zeros((n, n))

        for _ in range(NUM_ANTS):

            visited = [0]
            current = 0

            while len(visited) < n:

                probabilities = []

                for j in range(n):
                    if j not in visited:
                        tau = pheromone[current][j] ** ALPHA
                        eta = visibility[current][j] ** BETA
                        probabilities.append(tau * eta)
                    else:
                        probabilities.append(0)

                probabilities = np.array(probabilities)
                probabilities_sum = probabilities.sum()

                if probabilities_sum == 0:
                    break

                probabilities = probabilities / probabilities_sum
                next_node = np.random.choice(range(n), p=probabilities)

                visited.append(next_node)
                current = next_node

            if return_to_start:
                visited.append(0)

            total = 0
            for i in range(len(visited) - 1):
                # menghitung total cost rute
                total += cost_matrix[visited[i]][visited[i + 1]]

            if total < best_cost:
                best_cost = total
                best_route = visited

            # Simpan kontribusi pheromone ke delta 
            for i in range(len(visited) - 1):
                # update feromon
                delta_pheromone[visited[i]][visited[i + 1]] += Q / total

    # UPDATE GLOBAL 
    pheromone = (1 - EVAPORATION) * pheromone + delta_pheromone
  

    ordered_nodes = [nodes[i] for i in best_route]

    current = ordered_nodes[0]
    segments = []
    total_cost = 0
    total_distance = 0
    total_duration = 0

    for campus in ordered_nodes[1:]:

        dist, dur, route = get_osrm_route(
            LOCATIONS[current],
            LOCATIONS[campus],
            vehicle,
        )

        lights = count_lights_on_route(route, traffic_lights)
        traffic_delay = lights * TRAFFIC_LIGHT_DELAY

        cost = (
            (DISTANCE_WEIGHT * dist)
            + (TRAFFIC_WEIGHT * (dur + traffic_delay))
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

