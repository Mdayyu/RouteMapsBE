from app.config import DISTANCE_WEIGHT, TRAFFIC_WEIGHT, TRAFFIC_LIGHT_DELAY

def calculate_cost(distance, lights):
    traffic_time = lights * TRAFFIC_LIGHT_DELAY
    return (DISTANCE_WEIGHT * distance) + (TRAFFIC_WEIGHT * traffic_time)
