from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import time
from firebase_config import verify_token, get_firestore_db, initialize_firebase

app = FastAPI()

# Initialize Firebase
initialize_firebase()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODEL ---
class SystemStats(BaseModel):
    device_id: str
    user_id: str
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

class RemoteCommand(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = None

# In-memory storage (The "Mailbox") - Now organized by user_id and device_id
device_stats = {}  # Format: {user_id: {device_id: {...stats}}}

# Command queue for remote control - organized by user_id and device_id
command_queue = {}  # Format: {user_id: {device_id: [commands]}}

# Helper function to verify authentication
async def verify_auth(
    x_device_id: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
):
    """Verify device authentication - supports both device tokens and Firebase ID tokens"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing user ID")
    
    # For demo mode, allow demo-user/demo-token
    if x_user_id == "demo-user" and authorization == "Bearer demo-token":
        return {"user_id": x_user_id, "device_id": x_device_id or "demo-device"}
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
    
    token = authorization.split("Bearer ")[1]
    
    # Check if this is a device token (agent) or Firebase ID token (mobile app)
    # Device tokens are typically longer and URL-safe base64
    # Firebase ID tokens are JWT format (have dots)
    
    if "." in token:
        # This looks like a Firebase ID token (JWT format)
        user_info = verify_token(token)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid Firebase token")
        
        # For mobile app requests, user_id should match token
        # device_id is optional (used for targeting commands)
        return {"user_id": user_info.get("uid"), "device_id": x_device_id}
    else:
        # This is a device token - verify it exists for this user/device
        if not x_device_id:
            raise HTTPException(status_code=401, detail="Missing device ID for device token")
        
        try:
            db = get_firestore_db()
            if db:
                device_doc = db.collection('users').document(x_user_id).collection('devices').document(x_device_id).get()
                if device_doc.exists:
                    # Device is registered, allow access
                    return {"user_id": x_user_id, "device_id": x_device_id}
        except Exception as e:
            print(f"Warning: Could not verify device in Firestore: {e}")
        
        # If Firestore check fails or device not found, still allow for backward compatibility
        # In production, you should enforce strict validation
        print(f"⚠️ Warning: Device {x_device_id} for user {x_user_id} not verified in Firestore")
        return {"user_id": x_user_id, "device_id": x_device_id}

# --- ENDPOINT 1: RECEIVE DATA (POST) ---
@app.post("/api/update")
async def update_stats(stats: SystemStats, auth_info: dict = Depends(verify_auth)):
    user_id = auth_info["user_id"]
    device_id = auth_info["device_id"]
    
    # Initialize user storage if needed
    if user_id not in device_stats:
        device_stats[user_id] = {}
    
    # Store device stats
    device_stats[user_id][device_id] = {
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
    print(f"[API] Update from {user_id}/{device_id} - {os_name}{battery_info} | CPU: {stats.cpu}% | RAM: {stats.ram}%")
    
    # Optionally store in Firebase Firestore
    try:
        db = get_firestore_db()
        if db:
            db.collection('users').document(user_id).collection('devices').document(device_id).set({
                'last_update': time.time(),
                'status': 'Online',
                'system': stats.system,
                'battery': stats.battery
            }, merge=True)
    except Exception as e:
        print(f"Warning: Could not update Firestore: {e}")
    
    return {"message": "Data received successfully"}

# --- ENDPOINT 2: SEND DATA (GET) - Get stats for specific device ---
@app.get("/api/status")
async def get_stats(auth_info: dict = Depends(verify_auth)):
    user_id = auth_info["user_id"]
    device_id = auth_info["device_id"]
    
    if user_id in device_stats and device_id in device_stats[user_id]:
        return device_stats[user_id][device_id]
    
    return {"status": "Waiting for Agent...", "message": "No data available"}

# --- ENDPOINT 2B: Get all devices for a user ---
@app.get("/api/devices")
async def get_all_devices(auth_info: dict = Depends(verify_auth)):
    user_id = auth_info["user_id"]
    
    if user_id in device_stats:
        return {
            "devices": [
                {
                    "device_id": dev_id,
                    "stats": stats
                } 
                for dev_id, stats in device_stats[user_id].items()
            ]
        }
    
    return {"devices": []}

@app.get("/")
def root():
    return {"message": "System Monitor API", "status": "running"}

# --- ENDPOINT 3: SEND REMOTE COMMAND (POST) ---
@app.post("/api/command")
async def send_command(command: RemoteCommand, target_device_id: str, auth_info: dict = Depends(verify_auth)):
    user_id = auth_info["user_id"]
    
    # Initialize command queue for user if needed
    if user_id not in command_queue:
        command_queue[user_id] = {}
    if target_device_id not in command_queue[user_id]:
        command_queue[user_id][target_device_id] = []
    
    command_data = {
        "id": int(time.time() * 1000),  # Unique ID
        "command": command.command,
        "params": command.params or {},
        "timestamp": time.time(),
        "status": "pending"
    }
    command_queue[user_id][target_device_id].append(command_data)
    print(f"[API] Command received for {user_id}/{target_device_id}: {command.command}")
    return {"message": "Command queued successfully", "command_id": command_data["id"]}

# --- ENDPOINT 4: GET PENDING COMMANDS (GET) ---
@app.get("/api/commands")
async def get_commands(auth_info: dict = Depends(verify_auth)):
    user_id = auth_info["user_id"]
    device_id = auth_info["device_id"]
    
    if user_id not in command_queue or device_id not in command_queue[user_id]:
        return {"commands": []}
    
    # Return pending commands for this device
    pending = [cmd for cmd in command_queue[user_id][device_id] if cmd["status"] == "pending"]
    
    # Mark as sent
    for cmd in command_queue[user_id][device_id]:
        if cmd["status"] == "pending":
            cmd["status"] = "sent"
    
    return {"commands": pending}

# --- ENDPOINT 5: ACKNOWLEDGE COMMAND EXECUTION (POST) ---
@app.post("/api/command/ack/{command_id}")
async def acknowledge_command(command_id: int, success: bool = True, auth_info: dict = Depends(verify_auth)):
    user_id = auth_info["user_id"]
    device_id = auth_info["device_id"]
    
    if user_id in command_queue and device_id in command_queue[user_id]:
        command_queue[user_id][device_id] = [
            cmd for cmd in command_queue[user_id][device_id] if cmd["id"] != command_id
        ]
    
    print(f"[API] Command {command_id} acknowledged from {user_id}/{device_id}: {'Success' if success else 'Failed'}")
    return {"message": "Command acknowledged"}