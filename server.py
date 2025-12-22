from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

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
    cpu_details: Optional[Dict[str, Any]] = None
    ram_details: Optional[Dict[str, Any]] = None
    swap_details: Optional[Dict[str, Any]] = None
    gpu_details: Optional[List[Dict[str, Any]]] = None
    disk_details: Optional[Dict[str, Any]] = None
    disk_io: Optional[Dict[str, Any]] = None
    network: Optional[Dict[str, Any]] = None
    battery: Optional[Dict[str, Any]] = None
    system: Optional[Dict[str, Any]] = None
    processes: Optional[Dict[str, Any]] = None

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
        "cpu_details": stats.cpu_details,
        "ram_details": stats.ram_details,
        "swap_details": stats.swap_details,
        "gpu_details": stats.gpu_details,
        "disk_details": stats.disk_details,
        "disk_io": stats.disk_io,
        "network": stats.network,
        "battery": stats.battery,
        "system": stats.system,
        "processes": stats.processes,
        "status": "Online"
    }
    
    os_name = stats.system.get('os_name', 'Unknown') if stats.system else 'Unknown'
    battery_info = f" | Battery: {stats.battery['percent']}%" if stats.battery else ""
    print(f"[API] Update from {os_name}{battery_info} | CPU: {stats.cpu}% | RAM: {stats.ram}%")
    
    return {"message": "Data received successfully"}

# --- ENDPOINT 2: SEND DATA (GET) ---
@app.get("/api/status")
def get_stats():
    return current_stats

@app.get("/")
def root():
    return {"message": "System Monitor API", "status": "running"}