import psutil
import requests
import time
import GPUtil

# ADDRESS of the machine running server.py
# If running locally, use localhost. If server is on another PC, use its IP.
API_URL = "http://localhost:8000/api/update"

def start_agent():
    print(f"Agent started. Sending to {API_URL}...")

    while True:
        try:
            # 1. Gather Data
            cpu_usage = psutil.cpu_percent(interval=1)
            ram_usage = psutil.virtual_memory().percent

            gpus = GPUtil.getGPUs()
            gpu_usage = gpus[0].load * 100 if gpus else 0  # Convert to percentage


            
            disk_info = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    # Store each drive with its letter as key
                    drive_letter = partition.device.replace(':\\', '')
                    disk_info[drive_letter] = usage.percent
                except PermissionError:
                    # Skip drives that can't be accessed
                    continue

            # 2. Prepare Payload
            payload = {
                "cpu": cpu_usage,
                "ram": ram_usage,
                "gpu": gpu_usage,
                "disk": disk_info
            }


            # 3. Send to API
            response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                print(f"Sent: CPU {cpu_usage}%")
                print(f"Sent: ram {ram_usage}%")
                print(f"Sent: gpu {gpu_usage}%")
                for drive, usage in disk_info.items():
                    print(f"Sent: Drive {drive} Usage {usage}%")
            else:
                print(f"Server Error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print("Cannot connect to API. Is server.py running?")
        except Exception as e:
            print(f"Error: {e}")

        # Wait 2 seconds before next update
        time.sleep(2)

if __name__ == "__main__":
    start_agent()