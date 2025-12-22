from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODEL ---
class SystemStats(BaseModel):
    cpu: float
    ram: float
    gpu: float
    disk: Dict[str, float]

# In-memory storage (The "Mailbox")
current_stats = {
    "cpu": 0,
    "ram": 0,
    "gpu": 0,
    "disk": {},
    "status": "Waiting for Agent..."
}

# --- ENDPOINT 1: RECEIVE DATA (POST) ---
@app.post("/api/update")
def update_stats(stats: SystemStats):
    global current_stats
    current_stats = {
        "cpu": stats.cpu,
        "ram": stats.ram,
        "gpu": stats.gpu,
        "disk": stats.disk,
        "status": "Online"
    }
    print(f"[API] Received Update -> CPU: {stats.cpu}% | RAM: {stats.ram}% | GPU: {stats.gpu}% | Disk: {stats.disk}")
    return {"message": "Data received successfully"}

# --- ENDPOINT 2: SEND DATA (GET) ---
@app.get("/api/status")
def get_stats():
    return current_stats

@app.get("/")
def root():
    return {"message": "System Monitor API", "status": "running"}