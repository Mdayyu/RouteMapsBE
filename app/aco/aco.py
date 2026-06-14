import time

import numpy as np
import random
import os
import pandas as pd

results = []

from app.services.osrm_service import get_osrm_route
from app.services.traffic_service import (
    get_traffic_lights,
    count_lights_on_route,
)

np.set_printoptions(precision=3, suppress=True)

# ==============================
# LOAD DATASET
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(BASE_DIR, "data", "Locations_Yogyakarta.xlsx")

df = pd.read_excel(file_path)
df["Latitude"] = df["Latitude"].astype(str).str.replace(",", ".").astype(float)
df["Longitude"] = df["Longitude"].astype(str).str.replace(",", ".").astype(float)

#Membentuk Dictionary Lokasi
LOCATIONS = {
    row["Name"]: (row["Latitude"], row["Longitude"])
    for _, row in df.iterrows()
}

def run_aco(data: dict):
    start = "LLDIKTI"
    start_time = time.time()
    chosen = data.get("campuses", [])
    vehicle = data.get("vehicle", "mobil")
    return_to_start = data.get("returnToStart", False)

    if not chosen:
        return {}

    # ==============================
    # PARAMETER ACO
    # ==============================
    ALPHA = data.get('ALPHA', 1)
    BETA = data.get('BETA', 2)
    EVAPORATION = data.get('EVAPORATION', 0.5)
    QA = data.get('QA', 100)
    NUM_ANTS = data.get('NUM_ANTS', 50)
    NUM_ITERATIONS = data.get('NUM_ITERATIONS', 100)
    DISTANCE_WEIGHT = data.get('DISTANCE_WEIGHT', 0.5)
    TRAFFIC_WEIGHT = data.get('TRAFFIC_WEIGHT', 0.5)
    TRAFFIC_LIGHT_DELAY = data.get('TRAFFIC_LIGHT_DELAY', 2)

    nodes = [start] + chosen
    n = len(nodes)

    traffic_lights = get_traffic_lights(LOCATIONS[start], radius=1500)

    # ==============================
    # DISTANCE & TIME MATRIX
    # ==============================
    distance_matrix = np.zeros((n, n))
    time_matrix = np.zeros((n, n))

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
                total_time = dur + traffic_delay
                distance_matrix[i][j] = dist
                time_matrix[i][j] = total_time
            else:
                distance_matrix[i][j] = np.inf
                time_matrix[i][j] = np.inf

    # ==============================
    # NORMALISASI
    # ==============================
    dist_min = np.min(distance_matrix[np.isfinite(distance_matrix)])
    dist_max = np.max(distance_matrix[np.isfinite(distance_matrix)])
    time_min = np.min(time_matrix[np.isfinite(time_matrix)])
    time_max = np.max(time_matrix[np.isfinite(time_matrix)])
    

    distance_norm = (distance_matrix - dist_min) / (dist_max - dist_min + 1e-10)
    time_norm = (time_matrix - time_min) / (time_max - time_min + 1e-10)

    # ==============================
    # COST & VISIBILITY 
    # ==============================
    cost_matrix = (
        DISTANCE_WEIGHT * distance_norm +
        TRAFFIC_WEIGHT * time_norm
    )
    np.fill_diagonal(cost_matrix, np.inf)
    visibility = 1 / (cost_matrix + 1e-10)

    # ==============================
    # PHEROMONE
    # ==============================
    pheromone = np.ones((n, n))
    best_route = None
    best_cost = float("inf")

    # ==============================
    # ACO ITERATION
    # ==============================
    for iteration in range(NUM_ITERATIONS):
        delta_pheromone = np.zeros((n, n))
        for ant in range(NUM_ANTS):
            visited = [0]
            current = 0
            while len(visited) < n:
                probabilities = np.zeros(n)
                for j in range(n):
                    if j not in visited:
                        tau = pheromone[current][j] ** ALPHA
                        eta = visibility[current][j] ** BETA
                        probabilities[j] = tau * eta
                if probabilities.sum() == 0:
                    break
                probabilities = probabilities / probabilities.sum()
                if len(visited) == 1:
                    next_node = np.random.choice(range(n), p=probabilities)
                else:
                    next_node = np.argmax(probabilities)
                visited.append(next_node)
                current = next_node

            if return_to_start:
                visited.append(0)

            total_cost_route = sum(
                cost_matrix[visited[i]][visited[i+1]]
                for i in range(len(visited)-1)
            )

            # update best
            if total_cost_route < best_cost:
                best_cost = total_cost_route
                best_route = visited

            # update pheromone delta
            for i in range(len(visited) - 1):
                from_node = visited[i]
                to_node = visited[i + 1]
                delta = QA / (total_cost_route + 1e-10)
                delta_pheromone[from_node][to_node] += delta

        # update pheromone utama
        pheromone = (1 - EVAPORATION) * pheromone + delta_pheromone

    # ==============================
    # FINAL RESULT
    # ==============================
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
            DISTANCE_WEIGHT * dist +
            TRAFFIC_WEIGHT * (dur + traffic_delay)
        )
        segments.append({
            "from": current,
            "to": campus,
            "distance_km": round(dist, 2),
            "duration_min": round(dur + traffic_delay, 2),
            "traffic_lights": lights,
            "traffic_delay_min": round(traffic_delay, 1),
            "cost": round(cost, 2),
            "route": route,
        })
        total_cost += cost
        total_distance += dist
        total_duration += (dur + traffic_delay)
        current = campus

    end_time = time.time()
    execution_time = end_time - start_time
    print("EXEC TIME:", execution_time)
    print(f"- Number of Ants          : {NUM_ANTS}")
    print("====================================")
    print("ACO RESULT DEBUG")
    print("====================================")
    print("Best Cost:", best_cost)
    print("Best Route Index:", best_route)
    print(f"Total Jarak       : {round(total_distance, 2)} km")
    print(f"Total Waktu       : {round(total_duration, 2)} menit")

    # ubah index jadi nama lokasi biar kebaca
    ordered_nodes_debug = [nodes[i] for i in best_route]
    print("Best Route Name:", " -> ".join(ordered_nodes_debug))
    print("====================================")
    return {
        
        "total_distance_km": round(total_distance, 2),
        "total_duration_min": round(total_duration, 2),
        # "total_cost": round(total_cost, 2),
        "execution_time_sec": round(execution_time, 4), 
        "segments": segments,
    }