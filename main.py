from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.aco.aco import run_aco, LOCATIONS
app = FastAPI(title="ACO Route API")
from mangum import Mangum 

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
                
]

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Route untuk mendapatkan rute berdasarkan data input
@app.post("/route")
def get_route(data: dict):
    return run_aco(data)

# API Route untuk mendapatkan daftar kampus
@app.get("/campuses")
def get_campuses():
    return [
        {"key": key, "lat": lat, "lon": lon}
        for key, (lat, lon) in LOCATIONS.items()
        if key != "LLDIKTI"  # Tidak menampilkan kampus LLDIKTI
    ]

# API Route untuk mendapatkan parameter ACO
@app.get("/aco")
def get_parameter():
    return {
        "ALPHA": 1,
        "BETA": 3,
        "EVAPORATION": 0.5,
        "QA": 100,
        "NUM_ANTS": 50,
        "NUM_ITERATIONS": 100
    }