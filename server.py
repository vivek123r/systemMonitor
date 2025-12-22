from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# --- DATA MODEL ---
# This ensures the API only accepts valid data
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
# The Agent (PC) calls this to drop off data
@app.post("/api/update")
def update_stats(stats: SystemStats):
    global current_stats
    current_stats = {
        "cpu": stats.cpu,
        "ram": stats.ram,
        "gpu": stats.gpu,
        "disk":stats.disk,
        "status": "Online"
    }
    print(f"[API] Received Update -> CPU: {stats.cpu}% | RAM: {stats.ram}% | gpu: {stats.gpu}% | Disk: {stats.disk}")
    return {"message": "Data received successfully"}

# --- ENDPOINT 2: SEND DATA (GET) ---
# The Flutter App calls this to pick up data
@app.get("/api/status")
def get_stats():
    return current_stats

# Run with: uvicorn server:app --host 0.0.0.0 --port 8000