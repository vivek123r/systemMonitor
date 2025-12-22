import psutil
import requests
import time
import GPUtil
import platform
import subprocess
import os

# ADDRESS of the machine running server.py
API_URL = "https://system-monitor-silk.vercel.app/api/update"
COMMAND_URL = "https://system-monitor-silk.vercel.app/api/commands"
ACK_URL = "https://system-monitor-silk.vercel.app/api/command/ack"

def execute_command(command, params):
    """Execute remote commands received from server"""
    try:
        cmd_type = command.lower()
        
        # Power commands
        if cmd_type == "shutdown":
            print("⚠️ Executing SHUTDOWN...")
            os.system("shutdown /s /t 5")
            return True
            
        elif cmd_type == "restart":
            print("⚠️ Executing RESTART...")
            os.system("shutdown /r /t 5")
            return True
            
        elif cmd_type == "sleep":
            print("💤 Executing SLEEP...")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return True
            
        elif cmd_type == "logoff":
            print("👋 Executing LOGOFF...")
            os.system("shutdown /l")
            return True
            
        # Power profile commands
        elif cmd_type == "power_high":
            print("⚡ Setting power profile: High Performance")
            subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"])
            return True
            
        elif cmd_type == "power_balanced":
            print("⚖️ Setting power profile: Balanced")
            subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"])
            return True
            
        elif cmd_type == "power_saver":
            print("🔋 Setting power profile: Power Saver")
            subprocess.run(["powercfg", "/setactive", "a1841308-3541-4fab-bc81-f71556f20b4a"])
            return True
            
        # Brightness control
        elif cmd_type == "brightness":
            brightness = params.get("value", 50)
            print(f"💡 Setting brightness to {brightness}%")
            try:
                import screen_brightness_control as sbc
                sbc.set_brightness(brightness)
                return True
            except:
                print("⚠️ screen_brightness_control not installed. Install: pip install screen-brightness-control")
                return False
                
        # Application control
        elif cmd_type == "open_app":
            app = params.get("app", "")
            print(f"📂 Opening application: {app}")
            subprocess.Popen([app])
            return True
            
        elif cmd_type == "close_app":
            app = params.get("app", "")
            print(f"❌ Closing application: {app}")
            os.system(f"taskkill /IM {app} /F")
            return True
            
        # Screenshot
        elif cmd_type == "screenshot":
            print("📸 Taking screenshot...")
            try:
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                filename = f"screenshot_{int(time.time())}.png"
                screenshot.save(filename)
                print(f"✅ Screenshot saved: {filename}")
                return True
            except:
                print("⚠️ PIL not installed. Install: pip install pillow")
                return False
        
        else:
            print(f"❌ Unknown command: {command}")
            return False
            
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return False

def check_for_commands():
    """Check server for pending remote commands"""
    try:
        response = requests.get(COMMAND_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            commands = data.get("commands", [])
            
            for cmd in commands:
                cmd_id = cmd["id"]
                command = cmd["command"]
                params = cmd.get("params", {})
                
                print(f"\n🎮 Remote command received: {command}")
                success = execute_command(command, params)
                
                # Acknowledge command execution
                requests.post(f"{ACK_URL}/{cmd_id}", params={"success": success}, timeout=5)
                
    except Exception as e:
        pass  # Silently fail if server is unreachable

def start_agent():
    print(f"Agent started. Sending to {API_URL}...")

    while True:
        try:
            # 1. CPU Data (with details)
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_per_core = psutil.cpu_percent(interval=0, percpu=True)
            cpu_freq = psutil.cpu_freq()
            cpu_details = {
                "usage": cpu_usage,
                "per_core": cpu_per_core,
                "frequency_current": round(cpu_freq.current, 2) if cpu_freq else 0,
                "frequency_min": round(cpu_freq.min, 2) if cpu_freq else 0,
                "frequency_max": round(cpu_freq.max, 2) if cpu_freq else 0,
                "core_count_physical": psutil.cpu_count(logical=False),
                "core_count_logical": psutil.cpu_count(logical=True)
            }

            # 2. RAM Data (with details)
            ram = psutil.virtual_memory()
            ram_details = {
                "usage_percent": ram.percent,
                "total_gb": round(ram.total / (1024**3), 2),
                "used_gb": round(ram.used / (1024**3), 2),
                "available_gb": round(ram.available / (1024**3), 2),
                "free_gb": round(ram.free / (1024**3), 2)
            }
            
            # Swap memory
            swap = psutil.swap_memory()
            swap_details = {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "free_gb": round(swap.free / (1024**3), 2),
                "percent": swap.percent
            }

            # 3. GPU Data (with details)
            gpus = GPUtil.getGPUs()
            gpu_usage = gpus[0].load * 100 if gpus else 0
            gpu_details = []
            if gpus:
                for gpu in gpus:
                    gpu_details.append({
                        "id": gpu.id,
                        "name": gpu.name,
                        "load_percent": round(gpu.load * 100, 1),
                        "memory_used_mb": round(gpu.memoryUsed, 2),
                        "memory_total_mb": round(gpu.memoryTotal, 2),
                        "memory_free_mb": round(gpu.memoryFree, 2),
                        "memory_percent": round((gpu.memoryUsed / gpu.memoryTotal) * 100, 1),
                        "temperature_c": gpu.temperature
                    })

            # 4. Disk Data (with details)
            disk_info = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    drive_letter = partition.device.replace(':\\', '')
                    disk_info[drive_letter] = {
                        "usage_percent": round(usage.percent, 1),
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "filesystem": partition.fstype,
                        "mount_point": partition.mountpoint
                    }
                except PermissionError:
                    continue
            
            # Disk I/O statistics
            disk_io = psutil.disk_io_counters()
            disk_io_details = {
                "read_mb": round(disk_io.read_bytes / (1024**2), 2),
                "write_mb": round(disk_io.write_bytes / (1024**2), 2),
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count,
                "read_time_ms": disk_io.read_time,
                "write_time_ms": disk_io.write_time
            }

            # 5. Network Data (with details)
            net_io = psutil.net_io_counters()
            network_details = {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errors_in": net_io.errin,
                "errors_out": net_io.errout,
                "drop_in": net_io.dropin,
                "drop_out": net_io.dropout
            }

            # 6. Battery Data (with details) - PRIMARY
            battery = psutil.sensors_battery()
            battery_details = None
            if battery:
                time_left = battery.secsleft
                if time_left == psutil.POWER_TIME_UNLIMITED:
                    time_left_str = "Charging/Plugged"
                    time_left_minutes = None
                elif time_left == psutil.POWER_TIME_UNKNOWN:
                    time_left_str = "Unknown"
                    time_left_minutes = None
                else:
                    time_left_minutes = round(time_left / 60, 1)
                    time_left_str = f"{time_left_minutes} minutes"
                
                battery_details = {
                    "percent": battery.percent,
                    "plugged": battery.power_plugged,
                    "time_left_minutes": time_left_minutes,
                    "time_left_str": time_left_str
                }

            # 7. System Information (with details) - PRIMARY
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = round(uptime_seconds / 3600, 1)
            
            # Get CPU model name (proper marketing name)
            cpu_model = None
            
            # Method 1: Try Windows Registry (most reliable)
            if platform.system() == "Windows":
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                        r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                    cpu_model = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
                    winreg.CloseKey(key)
                except:
                    pass
            
            # Method 2: Try WMIC if registry failed
            if not cpu_model:
                try:
                    import subprocess
                    result = subprocess.run(['wmic', 'cpu', 'get', 'name'], 
                                          capture_output=True, text=True, timeout=2, shell=True)
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        cpu_model = lines[1].strip()
                except:
                    pass
            
            # Method 3: Fallback to platform.processor()
            if not cpu_model or "Family" in str(cpu_model) or "Model" in str(cpu_model):
                cpu_model = platform.processor()
            
            # Final fallback
            if not cpu_model or cpu_model.strip() == "":
                cpu_model = f"{platform.machine()} Processor"
            
            # Get GPU model name
            gpu_model = "No GPU detected"
            if gpu_details:
                gpu_model = gpu_details[0]["name"]
            
            system_details = {
                "os_name": platform.system(),  # PRIMARY
                "os_version": platform.version(),
                "os_release": platform.release(),
                "hostname": platform.node(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "cpu_model": cpu_model,  # PRIMARY - CPU Model Name
                "gpu_model": gpu_model,  # PRIMARY - GPU Model Name
                "python_version": platform.python_version(),
                "uptime_hours": uptime_hours,
                "uptime_seconds": round(uptime_seconds),
                "boot_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time))
            }

            # 8. Process Information (Top 5 CPU and Memory)
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            top_cpu_processes = sorted(
                [p for p in processes if p['cpu_percent'] is not None], 
                key=lambda x: x['cpu_percent'], 
                reverse=True
            )[:5]
            
            top_memory_processes = sorted(
                [p for p in processes if p['memory_percent'] is not None], 
                key=lambda x: x['memory_percent'], 
                reverse=True
            )[:5]
            
            process_details = {
                "top_cpu": top_cpu_processes,
                "top_memory": top_memory_processes,
                "total_processes": len(processes)
            }

            # 9. Prepare Comprehensive Payload
            payload = {
                # Simple values for backward compatibility
                "cpu": cpu_usage,
                "ram": ram_details["usage_percent"],
                "gpu": gpu_usage,
                "disk": {k: v["usage_percent"] for k, v in disk_info.items()},
                
                # Detailed subcategories
                "cpu_details": cpu_details,
                "ram_details": ram_details,
                "swap_details": swap_details,
                "gpu_details": gpu_details,
                "disk_details": disk_info,
                "disk_io": disk_io_details,
                "network": network_details,
                "battery": battery_details,  # PRIMARY
                "system": system_details,     # PRIMARY (includes os_name)
                "processes": process_details
            }

            # 10. Send to API
            response = requests.post(API_URL, json=payload, timeout=10)

            if response.status_code == 200:
                print(f"✓ Sent Data:")
                print(f"  OS: {system_details['os_name']} | Uptime: {uptime_hours}h")
                if battery_details:
                    print(f"  Battery: {battery_details['percent']}% | {'Plugged' if battery_details['plugged'] else 'On Battery'} | {battery_details['time_left_str']}")
                print(f"  CPU: {cpu_usage}% ({cpu_details['core_count_logical']} cores @ {cpu_details['frequency_current']} MHz)")
                print(f"  RAM: {ram_details['usage_percent']}% ({ram_details['used_gb']}/{ram_details['total_gb']} GB)")
                print(f"  GPU: {gpu_usage}%" + (f" ({gpu_details[0]['name']})" if gpu_details else ""))
                print(f"  Network: ↓{network_details['bytes_recv_mb']}MB ↑{network_details['bytes_sent_mb']}MB")
                for drive, details in disk_info.items():
                    print(f"  Drive {drive}: {details['usage_percent']}% ({details['used_gb']}/{details['total_gb']} GB)")
            else:
                print(f"✗ Server Error: {response.status_code}")
                
            # Check for remote commands
            check_for_commands()

        except requests.exceptions.ConnectionError:
            print("✗ Cannot connect to API. Check internet connection.")
        except requests.exceptions.Timeout:
            print("✗ Request timed out.")
        except Exception as e:
            print(f"✗ Error: {e}")

        # Wait 2 seconds before next update
        time.sleep(2)

if __name__ == "__main__":
    start_agent()