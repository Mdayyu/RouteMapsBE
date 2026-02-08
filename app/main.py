from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.aco.aco import run_aco
from app.data.locations import LOCATIONS

app = FastAPI(title="ACO Route API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/route")
def get_route(data: dict):
    return run_aco(data)

@app.get("/campuses")
def get_campuses():
    return [
        {"key": key, "lat": lat, "lon": lon}
        for key, (lat, lon) in LOCATIONS.items()
        if key != "LLDIKTI"
    ]
