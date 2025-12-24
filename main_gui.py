"""
System Monitor GUI Application
Modern interface with device registration and real-time monitoring
"""
import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import psutil
import GPUtil
import platform
import os
import uuid
import secrets
from dotenv import load_dotenv
from firebase_config import get_firestore_db, initialize_firebase
import requests

# Suppress agent.py warnings during import
import sys
from io import StringIO
old_stdout = sys.stdout
sys.stdout = StringIO()

# Import functions from existing files without modification
from agent import execute_command, check_for_commands

sys.stdout = old_stdout

load_dotenv()

class RegistrationWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        
        self.on_success = on_success
        self.title("System Monitor - Setup Wizard")
        self.geometry("600x600")
        self.transient(parent)
        self.grab_set()
        
        # Prevent closing
        self.protocol("WM_DELETE_WINDOW", self.on_close_attempt)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"600x600+{x}+{y}")
        
        self.current_step = 2  # Start directly at registration
        self.setup_ui()
    
    def on_close_attempt(self):
        """Prevent closing without completing setup"""
        response = messagebox.askyesno(
            "Exit Setup?",
            "You need to complete registration to use the app.\n\nAre you sure you want to exit?"
        )
        if response:
            self.destroy()
            self.master.quit()
    
    def setup_ui(self):
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header with steps
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(header_frame, text="System Monitor - Setup Wizard", 
                    font=("Arial", 20, "bold")).pack(pady=15)
        
        # Step indicator
        step_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        step_frame.pack(pady=(0, 15))
        
        steps = ["Registration", "Complete"]
        for i, step in enumerate(steps, 1):
            display_step = i + 1  # Offset for display
            color = "#1f6aa5" if display_step == self.current_step else "gray30"
            text_color = "white" if display_step == self.current_step else "gray"
            
            step_btn = ctk.CTkButton(step_frame, text=f"{i}. {step}", 
                                    width=150, height=30,
                                    fg_color=color,
                                    state="disabled")
            step_btn.pack(side="left", padx=5)
        
        # Content based on step
        if self.current_step == 2:
            self.show_registration_step()
        elif self.current_step == 3:
            self.show_complete_step()
    
    def show_welcome_step(self):
        """Step 1: Welcome screen"""
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        ctk.CTkLabel(content_frame, text="👋 Welcome!", 
                    font=("Arial", 32, "bold")).pack(pady=(40, 20))
        
        ctk.CTkLabel(content_frame, 
                    text="System Monitor allows you to:",
                    font=("Arial", 14, "bold"),
                    anchor="w").pack(pady=(20, 10), padx=40, fill="x")
        
        features = [
            "📊 Monitor your PC in real-time",
            "📱 Control your PC from mobile app",
            "🔄 Sync data across devices",
            "🔐 Secure device authentication"
        ]
        
        for feature in features:
            ctk.CTkLabel(content_frame, text=feature, 
                        font=("Arial", 13),
                        anchor="w").pack(pady=5, padx=60, fill="x")
        
        ctk.CTkLabel(content_frame, 
                    text="Let's get your device set up!",
                    font=("Arial", 12),
                    text_color="gray").pack(pady=(30, 20))
        
        # Navigation
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20, padx=30)
        
        ctk.CTkButton(btn_frame, text="Get Started →", 
                     command=lambda: self.next_step(),
                     height=45,
                     font=("Arial", 14, "bold"),
                     fg_color="#1f6aa5",
                     hover_color="#144870").pack(side="right")
    
    def show_registration_step(self):
        """Step 2: Registration form"""
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        ctk.CTkLabel(content_frame, text="🔐 Device Registration", 
                    font=("Arial", 22, "bold")).pack(pady=(10, 5))
        
        ctk.CTkLabel(content_frame, 
                    text="Connect this PC to your account",
                    font=("Arial", 11),
                    text_color="gray").pack(pady=(0, 15))
        
        # User ID
        ctk.CTkLabel(content_frame, text="User ID:", 
                    font=("Arial", 11, "bold"),
                    anchor="w").pack(pady=(5, 3), padx=20, fill="x")
        
        self.user_id_entry = ctk.CTkEntry(content_frame, 
                                          placeholder_text="Enter your Firebase User ID",
                                          height=38)
        self.user_id_entry.pack(pady=3, padx=20, fill="x")
        
        ctk.CTkLabel(content_frame, 
                    text="📱 Find in mobile app: Profile > Settings > User ID",
                    font=("Arial", 9),
                    text_color="gray",
                    anchor="w").pack(padx=20, fill="x")
        
        # Device Name
        ctk.CTkLabel(content_frame, text="Device Name:", 
                    font=("Arial", 11, "bold"),
                    anchor="w").pack(pady=(10, 3), padx=20, fill="x")
        
        default_name = f"{platform.system()} - {platform.node()}"
        self.device_name_entry = ctk.CTkEntry(content_frame, 
                                              placeholder_text="My Computer",
                                              height=38)
        self.device_name_entry.insert(0, default_name)
        self.device_name_entry.pack(pady=3, padx=20, fill="x")
        
        ctk.CTkLabel(content_frame, 
                    text="💻 Give your PC a friendly name",
                    font=("Arial", 9),
                    text_color="gray",
                    anchor="w").pack(padx=20, fill="x")
        
        # Status label
        self.status_label = ctk.CTkLabel(content_frame, text="", 
                                        font=("Arial", 11))
        self.status_label.pack(pady=10)
        
        # Navigation - make sure it's always visible
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=15, padx=30)
        
        ctk.CTkButton(btn_frame, text="⏭️ Skip (Demo)", 
                     command=self.skip_registration,
                     height=50,
                     font=("Arial", 14, "bold"),
                     fg_color="gray40",
                     hover_color="gray30",
                     width=180).pack(side="left")
        
        ctk.CTkButton(btn_frame, text="Register Device →", 
                     command=self.register_device,
                     height=50,
                     font=("Arial", 14, "bold"),
                     fg_color="#1f6aa5",
                     hover_color="#144870",
                     width=200).pack(side="right")
    
    def show_complete_step(self):
        """Step 3: Completion screen"""
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        ctk.CTkLabel(content_frame, text="✅", 
                    font=("Arial", 56)).pack(pady=(30, 15))
        
        ctk.CTkLabel(content_frame, text="Setup Complete!", 
                    font=("Arial", 24, "bold")).pack(pady=8)
        
        ctk.CTkLabel(content_frame, 
                    text="Your device has been successfully registered.",
                    font=("Arial", 12),
                    text_color="gray").pack(pady=5)
        
        # Device info
        info_frame = ctk.CTkFrame(content_frame, fg_color="#2b2b2b")
        info_frame.pack(pady=20, padx=40, fill="x")
        
        device_id = os.getenv("DEVICE_ID", "Unknown")
        user_id = os.getenv("USER_ID", "Unknown")
        
        ctk.CTkLabel(info_frame, text="Device ID:", 
                    font=("Arial", 10),
                    text_color="gray",
                    anchor="w").pack(pady=(12, 2), padx=20, fill="x")
        ctk.CTkLabel(info_frame, text=device_id[:24] + "...", 
                    font=("Arial", 10, "bold"),
                    anchor="w").pack(pady=(0, 8), padx=20, fill="x")
        
        ctk.CTkLabel(info_frame, text="User ID:", 
                    font=("Arial", 10),
                    text_color="gray",
                    anchor="w").pack(pady=(5, 2), padx=20, fill="x")
        ctk.CTkLabel(info_frame, text=user_id, 
                    font=("Arial", 10, "bold"),
                    anchor="w").pack(pady=(0, 12), padx=20, fill="x")
        
        ctk.CTkLabel(content_frame, 
                    text="🎉 You can now monitor and control your PC remotely!",
                    font=("Arial", 11),
                    text_color="lime").pack(pady=8)
        
        # Navigation - pinned to bottom
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=15, padx=30)
        
        ctk.CTkButton(btn_frame, text="Start Monitoring →", 
                     command=self.complete_registration,
                     height=50,
                     font=("Arial", 14, "bold"),
                     fg_color="#1f6aa5",
                     hover_color="#144870").pack(expand=True, fill="x")
    
    def next_step(self):
        """Go to next step"""
        self.current_step += 1
        self.setup_ui()
    
    def previous_step(self):
        """Go to previous step"""
        self.current_step -= 1
        self.setup_ui()
    def skip_registration(self):
        """Use demo credentials"""
        response = messagebox.askyesno(
            "Demo Mode",
            "Demo mode uses temporary credentials.\n\n" +
            "Features:\n" +
            "✓ Local monitoring works\n" +
            "✗ No mobile app sync\n" +
            "✗ Data not saved to cloud\n\n" +
            "Continue with demo mode?"
        )
        
        if response:
            env_content = f"""# Device Configuration (DEMO MODE)
DEVICE_ID={uuid.uuid4()}
USER_ID=demo-user
DEVICE_TOKEN=demo-token

# Demo credentials - register properly for full features
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            
            load_dotenv(override=True)
            self.next_step()
    
    def register_device(self):
        user_id = self.user_id_entry.get().strip()
        device_name = self.device_name_entry.get().strip()
        
        if not user_id:
            self.status_label.configure(text="❌ User ID is required", text_color="red")
            return
        
        if not device_name:
            device_name = f"{platform.system()} - {platform.node()}"
        
        self.status_label.configure(text="⏳ Registering device...", text_color="orange")
        self.update()
        
        try:
            # Generate credentials
            device_id = str(uuid.uuid4())
            device_token = secrets.token_urlsafe(32)
            
            # Try to register in Firestore
            try:
                if initialize_firebase():
                    db = get_firestore_db()
                    device_doc = db.collection('users').document(user_id).collection('devices').document(device_id)
                    device_doc.set({
                        'device_id': device_id,
                        'device_name': device_name,
                        'created_at': time.time(),
                        'status': 'registered',
                        'token_hash': secrets.token_hex(16)
                    })
            except Exception as e:
                print(f"Warning: Could not register in Firestore: {e}")
            
            # Save to .env file
            env_content = f"""# Device Configuration
DEVICE_ID={device_id}
USER_ID={user_id}
DEVICE_TOKEN={device_token}

# Generated by System Monitor GUI
# Keep this file secure
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            
            # Reload environment
            load_dotenv(override=True)
            
            self.status_label.configure(text="✅ Registration successful!", text_color="lime")
            self.after(800, lambda: self.next_step())
            
        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {str(e)}", text_color="red")
    
    def complete_registration(self):
        self.destroy()
        self.on_success()


class SystemMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("System Monitor")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"1000x700+{x}+{y}")
        
        # Agent thread
        self.agent_thread = None
        self.agent_running = False
        
        # Check registration - show wizard if not registered
        load_dotenv()
        if not os.getenv("DEVICE_ID") or os.getenv("DEVICE_ID") == "":
            self.after(100, self.show_registration)
        else:
            self.setup_main_ui()
            self.start_monitoring()
    
    def show_registration(self):
        """Show registration window"""
        RegistrationWindow(self, self.on_registration_complete)
    
    def on_registration_complete(self):
        """Called after successful registration"""
        load_dotenv(override=True)
        self.setup_main_ui()
        self.start_monitoring()
    
    def setup_main_ui(self):
        """Setup main dashboard UI with modern design"""
        
        # Gradient-style Header
        header = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#0d1117")
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Logo and title
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.pack(side="left", padx=25, pady=15)
        
        ctk.CTkLabel(logo_frame, text="⚡", font=("Segoe UI Emoji", 32)).pack(side="left", padx=(0, 10))
        
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left")
        ctk.CTkLabel(title_frame, text="System Monitor", 
                    font=("Segoe UI", 24, "bold"), text_color="#58a6ff").pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Real-time PC Monitoring", 
                    font=("Segoe UI", 11), text_color="#8b949e").pack(anchor="w")
        
        # Status badge
        status_frame = ctk.CTkFrame(header, fg_color="#238636", corner_radius=15)
        status_frame.pack(side="right", padx=25, pady=25)
        
        self.status_indicator = ctk.CTkLabel(status_frame, text="● ", 
                                            text_color="white", 
                                            font=("Segoe UI", 12))
        self.status_indicator.pack(side="left", padx=(12, 0), pady=6)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Connected", 
                                         font=("Segoe UI", 11, "bold"),
                                         text_color="white")
        self.status_label.pack(side="left", padx=(0, 12), pady=6)
        
        # Main container with scrollable frame
        main_container = ctk.CTkScrollableFrame(self, fg_color="#0d1117")
        main_container.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Grid layout - 2 columns
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        
        # Row 0: System Info Card
        info_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color="#161b22", border_width=1, border_color="#30363d")
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=8)
        
        # Info header
        info_header = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_header.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(info_header, text="🖥️", font=("Segoe UI Emoji", 20)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(info_header, text="System Information", font=("Segoe UI", 16, "bold"), text_color="#c9d1d9").pack(side="left")
        
        info_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        device_id = os.getenv("DEVICE_ID", "Unknown")
        self.info_labels = {}
        self.info_labels['device'] = self.create_info_row(info_content, "🔑 Device ID", device_id[:20] + "...")
        self.info_labels['os'] = self.create_info_row(info_content, "💿 Operating System", f"{platform.system()} {platform.release()}")
        self.info_labels['hostname'] = self.create_info_row(info_content, "🏠 Hostname", platform.node())
        self.info_labels['processor'] = self.create_info_row(info_content, "⚙️ Processor", platform.processor()[:40] + "...")
        
        # Row 1: CPU and RAM with progress bars
        self.cpu_frame = self.create_metric_card_with_progress(main_container, "🔥", "CPU Usage", "0%", "#f97316")
        self.cpu_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=8)
        
        self.ram_frame = self.create_metric_card_with_progress(main_container, "🧠", "RAM Usage", "0%", "#8b5cf6")
        self.ram_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=8)
        
        # Row 2: GPU and Disk
        self.gpu_frame = self.create_metric_card_with_progress(main_container, "🎮", "GPU Usage", "0%", "#10b981")
        self.gpu_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=8)
        
        self.disk_frame = self.create_metric_card_with_progress(main_container, "💾", "Disk Usage", "0%", "#3b82f6")
        self.disk_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=8)
        
        # Row 3: Network and Battery
        self.network_frame = self.create_metric_card_with_progress(main_container, "🌐", "Network", "0 MB", "#06b6d4")
        self.network_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=8)
        
        self.battery_frame = self.create_metric_card_with_progress(main_container, "🔋", "Battery", "N/A", "#22c55e")
        self.battery_frame.grid(row=3, column=1, sticky="nsew", padx=5, pady=8)
        
        # Configure row weights
        for i in range(4):
            main_container.grid_rowconfigure(i, weight=1)
    
    def create_card(self, parent, title):
        """Create a card container"""
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#161b22", border_width=1, border_color="#30363d")
        
        title_label = ctk.CTkLabel(card, text=title, 
                                   font=("Segoe UI", 16, "bold"),
                                   text_color="#c9d1d9",
                                   anchor="w")
        title_label.pack(fill="x", padx=15, pady=(15, 5))
        
        return card
    
    def create_info_row(self, parent, label, value):
        """Create an info row with modern styling"""
        row = ctk.CTkFrame(parent, fg_color="#21262d", corner_radius=8)
        row.pack(fill="x", pady=4)
        
        ctk.CTkLabel(row, text=label, 
                    font=("Segoe UI", 11),
                    text_color="#8b949e",
                    anchor="w").pack(side="left", padx=12, pady=8)
        
        value_label = ctk.CTkLabel(row, text=value, 
                                   font=("Segoe UI", 11, "bold"),
                                   text_color="#c9d1d9",
                                   anchor="e")
        value_label.pack(side="right", padx=12, pady=8)
        
        return value_label
    
    def create_metric_card_with_progress(self, parent, icon, title, initial_value, color):
        """Create a metric card with icon, progress bar, and modern design"""
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#161b22", border_width=1, border_color="#30363d")
        
        # Header with icon
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(18, 5))
        
        ctk.CTkLabel(header_frame, text=icon, font=("Segoe UI Emoji", 24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_frame, text=title, font=("Segoe UI", 14, "bold"), text_color="#8b949e").pack(side="left")
        
        # Large value display
        value_label = ctk.CTkLabel(card, text=initial_value, 
                                   font=("Segoe UI", 42, "bold"),
                                   text_color=color)
        value_label.pack(pady=(10, 8))
        
        # Progress bar
        progress = ctk.CTkProgressBar(card, width=200, height=8, corner_radius=4,
                                       fg_color="#21262d", progress_color=color)
        progress.pack(pady=(0, 10))
        progress.set(0)
        
        # Details label
        details_label = ctk.CTkLabel(card, text="Loading...", 
                                     font=("Segoe UI", 10),
                                     text_color="#6e7681")
        details_label.pack(fill="x", padx=20, pady=(0, 18))
        
        # Store references
        card.value_label = value_label
        card.progress = progress
        card.details_label = details_label
        card.color = color
        
        return card
    
    def get_status_color(self, percent):
        """Return color based on usage percentage"""
        if percent < 50:
            return "#22c55e"  # Green
        elif percent < 80:
            return "#f59e0b"  # Yellow/Orange
        else:
            return "#ef4444"  # Red
    
    def create_metric_card(self, parent, title, initial_value):
        """Create a metric card with large value display (legacy)"""
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#161b22", border_width=1, border_color="#30363d")
        
        title_label = ctk.CTkLabel(card, text=title, 
                                   font=("Segoe UI", 14, "bold"),
                                   text_color="#8b949e",
                                   anchor="w")
        title_label.pack(fill="x", padx=20, pady=(20, 10))
        
        value_label = ctk.CTkLabel(card, text=initial_value, 
                                   font=("Segoe UI", 36, "bold"),
                                   text_color="#58a6ff")
        value_label.pack(expand=True, pady=20)
        
        details_label = ctk.CTkLabel(card, text="", 
                                     font=("Segoe UI", 10),
                                     text_color="#6e7681")
        details_label.pack(fill="x", padx=20, pady=(0, 15))
        
        # Store references
        card.value_label = value_label
        card.details_label = details_label
        
        return card
    
    def start_monitoring(self):
        """Start the monitoring agent in background thread"""
        self.agent_running = True
        self.agent_thread = threading.Thread(target=self.agent_loop, daemon=True)
        self.agent_thread.start()
        
        # Start UI update loop
        self.update_ui_loop()
    
    def agent_loop(self):
        """Background thread running the agent - EXACT COPY of agent.py logic"""
        API_URL = "https://system-monitor-silk.vercel.app/api/update"
        COMMAND_URL = "https://system-monitor-silk.vercel.app/api/commands"
        ACK_URL = "https://system-monitor-silk.vercel.app/api/command/ack"
        
        while self.agent_running:
            try:
                # Get credentials from environment
                device_id = os.getenv("DEVICE_ID")
                user_id = os.getenv("USER_ID")
                device_token = os.getenv("DEVICE_TOKEN")
                
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

                # 6. Battery Data (with details)
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

                # 7. System Information (with details)
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time
                uptime_hours = round(uptime_seconds / 3600, 1)
                
                # Get CPU model name
                cpu_model = None
                if platform.system() == "Windows":
                    try:
                        import winreg
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                        cpu_model = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
                        winreg.CloseKey(key)
                    except:
                        pass
                
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
                
                if not cpu_model or "Family" in str(cpu_model) or "Model" in str(cpu_model):
                    cpu_model = platform.processor()
                
                if not cpu_model or cpu_model.strip() == "":
                    cpu_model = f"{platform.machine()} Processor"
                
                # Get GPU model name
                gpu_model = "No GPU detected"
                if gpu_details:
                    gpu_model = gpu_details[0]["name"]
                
                system_details = {
                    "os_name": platform.system(),
                    "os_version": platform.version(),
                    "os_release": platform.release(),
                    "hostname": platform.node(),
                    "architecture": platform.machine(),
                    "processor": platform.processor(),
                    "cpu_model": cpu_model,
                    "gpu_model": gpu_model,
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

                # 9. Prepare Comprehensive Payload (EXACT same as agent.py)
                payload = {
                    # Authentication
                    "device_id": device_id,
                    "user_id": user_id,
                    
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
                    "battery": battery_details,
                    "system": system_details,
                    "processes": process_details
                }

                # 10. Send to API with authentication headers
                headers = {
                    "X-Device-ID": device_id,
                    "X-User-ID": user_id,
                    "Authorization": f"Bearer {device_token}"
                }
                response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"✓ Data sent - CPU: {cpu_usage}% | RAM: {ram_details['usage_percent']}%")
                    self.update_status(True)
                else:
                    print(f"✗ Server Error: {response.status_code}")
                    self.update_status(False)
                
                # Check for remote commands
                try:
                    cmd_headers = {
                        "X-Device-ID": device_id,
                        "X-User-ID": user_id,
                        "Authorization": f"Bearer {device_token}"
                    }
                    cmd_response = requests.get(COMMAND_URL, headers=cmd_headers, timeout=5)
                    if cmd_response.status_code == 200:
                        cmd_data = cmd_response.json()
                        commands = cmd_data.get("commands", [])
                        
                        for cmd in commands:
                            cmd_id = cmd["id"]
                            command = cmd["command"]
                            params = cmd.get("params", {})
                            
                            print(f"🎮 Remote command: {command}")
                            success = execute_command(command, params)
                            
                            # Acknowledge command execution
                            requests.post(f"{ACK_URL}/{cmd_id}", headers=cmd_headers, 
                                        params={"success": success}, timeout=5)
                except:
                    pass
                
            except requests.exceptions.ConnectionError:
                print("✗ Cannot connect to API")
                self.update_status(False)
            except requests.exceptions.Timeout:
                print("✗ Request timed out")
                self.update_status(False)
            except Exception as e:
                print(f"Agent error: {e}")
                self.update_status(False)
            
            time.sleep(2)
    
    def update_status(self, connected):
        """Update connection status indicator with badge styling"""
        try:
            if connected:
                self.status_indicator.configure(text_color="white")
                self.status_label.configure(text="Connected")
                self.status_indicator.master.configure(fg_color="#238636")  # Green badge
            else:
                self.status_indicator.configure(text_color="white")
                self.status_label.configure(text="Disconnected")
                self.status_indicator.master.configure(fg_color="#da3633")  # Red badge
        except:
            pass
    
    def update_ui_loop(self):
        """Update UI with current system stats and progress bars"""
        try:
            # CPU - with progress bar and dynamic color
            cpu = psutil.cpu_percent(interval=0)
            cpu_color = self.get_status_color(cpu)
            self.cpu_frame.value_label.configure(text=f"{cpu:.1f}%", text_color=cpu_color)
            self.cpu_frame.progress.set(cpu / 100)
            self.cpu_frame.progress.configure(progress_color=cpu_color)
            cores = psutil.cpu_count(logical=False)
            threads = psutil.cpu_count(logical=True)
            freq = psutil.cpu_freq()
            freq_text = f" @ {freq.current:.0f} MHz" if freq else ""
            self.cpu_frame.details_label.configure(text=f"{cores} cores • {threads} threads{freq_text}")
            
            # RAM - with progress bar and dynamic color
            ram = psutil.virtual_memory()
            ram_color = self.get_status_color(ram.percent)
            self.ram_frame.value_label.configure(text=f"{ram.percent:.1f}%", text_color=ram_color)
            self.ram_frame.progress.set(ram.percent / 100)
            self.ram_frame.progress.configure(progress_color=ram_color)
            self.ram_frame.details_label.configure(
                text=f"{ram.used / (1024**3):.1f} GB / {ram.total / (1024**3):.1f} GB used"
            )
            
            # GPU - with progress bar
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_percent = gpu.load * 100
                gpu_color = self.get_status_color(gpu_percent)
                self.gpu_frame.value_label.configure(text=f"{gpu_percent:.1f}%", text_color=gpu_color)
                self.gpu_frame.progress.set(gpu_percent / 100)
                self.gpu_frame.progress.configure(progress_color=gpu_color)
                self.gpu_frame.details_label.configure(
                    text=f"{gpu.name[:25]} • {gpu.temperature}°C"
                )
            else:
                self.gpu_frame.value_label.configure(text="N/A", text_color="#6e7681")
                self.gpu_frame.progress.set(0)
                self.gpu_frame.details_label.configure(text="No GPU detected")
            
            # Disk - with progress bar and dynamic color
            disk = psutil.disk_usage('/')
            disk_color = self.get_status_color(disk.percent)
            self.disk_frame.value_label.configure(text=f"{disk.percent:.1f}%", text_color=disk_color)
            self.disk_frame.progress.set(disk.percent / 100)
            self.disk_frame.progress.configure(progress_color=disk_color)
            self.disk_frame.details_label.configure(
                text=f"{disk.used / (1024**3):.0f} GB / {disk.total / (1024**3):.0f} GB used"
            )
            
            # Network - show transfer rate
            net = psutil.net_io_counters()
            total_mb = (net.bytes_sent + net.bytes_recv) / (1024**2)
            if total_mb > 1024:
                self.network_frame.value_label.configure(text=f"{total_mb/1024:.1f} GB", text_color="#06b6d4")
            else:
                self.network_frame.value_label.configure(text=f"{total_mb:.0f} MB", text_color="#06b6d4")
            self.network_frame.progress.set(min(total_mb / 10000, 1.0))  # Scale for visual
            self.network_frame.details_label.configure(
                text=f"↑ {net.bytes_sent / (1024**2):.1f} MB  •  ↓ {net.bytes_recv / (1024**2):.1f} MB"
            )
            
            # Battery - with progress bar
            battery = psutil.sensors_battery()
            if battery:
                batt_color = "#22c55e" if battery.percent > 20 else "#ef4444"
                if battery.power_plugged:
                    batt_color = "#22c55e"
                    status = "⚡ Plugged in"
                else:
                    status = "🔋 On battery"
                self.battery_frame.value_label.configure(text=f"{battery.percent:.0f}%", text_color=batt_color)
                self.battery_frame.progress.set(battery.percent / 100)
                self.battery_frame.progress.configure(progress_color=batt_color)
                self.battery_frame.details_label.configure(text=status)
            else:
                self.battery_frame.value_label.configure(text="N/A", text_color="#6e7681")
                self.battery_frame.progress.set(0)
                self.battery_frame.details_label.configure(text="Desktop PC • No battery")
            
        except Exception as e:
            print(f"UI update error: {e}")
        
        # Schedule next update
        self.after(1000, self.update_ui_loop)
    
    def on_closing(self):
        """Handle window closing"""
        self.agent_running = False
        if self.agent_thread:
            self.agent_thread.join(timeout=2)
        self.destroy()


def main():
    app = SystemMonitorApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
