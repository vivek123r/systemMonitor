# System Monitor GUI Application

Modern desktop application with device registration and real-time system monitoring.

## Features

✅ **Device Registration Flow**
- First-time setup wizard
- Firebase integration
- Secure credential generation
- Demo mode for testing

✅ **Real-time System Monitoring**
- CPU usage and details
- RAM and Swap memory
- GPU monitoring
- Disk usage and I/O
- Network statistics
- Battery status

✅ **Remote Control**
- Receives commands from mobile app
- Shares data with mobile app
- Real-time synchronization

## Installation

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the GUI Application**
```bash
python main_gui.py
```

## First Time Setup

### Option 1: Proper Registration (Recommended)

1. Launch the app: `python main_gui.py`
2. Registration window will appear
3. Enter your **User ID** from the mobile app:
   - Open mobile app
   - Go to Profile/Settings
   - Copy your User ID
4. Enter a device name (e.g., "My Laptop", "Gaming PC")
5. Click "Register Device"
6. Credentials will be saved to `.env` file

### Option 2: Demo Mode (Testing)

1. Launch the app: `python main_gui.py`
2. Click "Skip (Demo Mode)"
3. App will run with temporary credentials
4. Data won't sync with mobile app

## Usage

### Dashboard

The main window displays:

- **System Information**: Device ID, OS, hostname, processor
- **CPU Usage**: Real-time percentage, cores, threads
- **RAM Usage**: Memory percentage, used/total
- **GPU Usage**: GPU load and temperature
- **Disk Usage**: Space percentage, used/total
- **Network**: Total data sent/received
- **Battery**: Percentage and charging status

### Connection Status

- **Green dot (●)**: Connected to server
- **Red dot (●)**: Disconnected

### Background Agent

The app automatically:
- Sends system data to server every 2 seconds
- Checks for remote commands
- Updates the UI in real-time

## File Structure

```
systemMonitor/
├── main_gui.py          ← GUI APPLICATION (NEW)
├── agent.py             ← Background agent (unchanged)
├── device_register.py   ← Registration helper (unchanged)
├── server.py            ← API server (unchanged)
├── requirements.txt     ← Updated with GUI deps
├── .env                 ← Generated credentials
└── GUI_README.md        ← This file
```

## How It Works

```
┌─────────────────────────┐
│   Desktop GUI App       │
│   (main_gui.py)         │
│                         │
│  ┌──────────────────┐   │
│  │ Registration     │   │
│  │ Dialog           │   │
│  └──────────────────┘   │
│          ↓              │
│  ┌──────────────────┐   │
│  │ Main Dashboard   │   │
│  │ - Live Metrics   │   │
│  │ - System Info    │   │
│  └──────────────────┘   │
│          ↕              │
│  Background Thread      │
│  (sends data every 2s)  │
└─────────────────────────┘
            ↕
    ┌──────────────┐
    │  API Server  │
    │   (Vercel)   │
    └──────────────┘
            ↕
    ┌──────────────┐
    │  Mobile App  │
    │  (Flutter)   │
    └──────────────┘
```

## Command Line vs GUI

You can still run the original command-line agent:

```bash
# Command line (original)
python agent.py

# GUI application (new)
python main_gui.py
```

Both do the same thing, but GUI provides:
- Visual interface
- Built-in registration
- No terminal required
- Better user experience

## Troubleshooting

### "Module not found: customtkinter"
```bash
pip install customtkinter
```

### Registration fails
- Check internet connection
- Verify Firebase credentials in `firebase-service-account.json`
- Try demo mode for testing

### Window doesn't appear
- Check if Python has GUI permissions
- On Windows: Run as administrator if needed
- Try different display scaling

### Agent not sending data
- Check `.env` file exists
- Verify DEVICE_ID is set
- Check firewall settings
- Ensure API server is running

## Customization

### Change Update Interval

Edit [main_gui.py](main_gui.py#L487):
```python
time.sleep(2)  # Change to 5 for 5 seconds
```

### Change Window Size

Edit [main_gui.py](main_gui.py#L215):
```python
self.geometry("1000x700")  # Change dimensions
```

### Change Theme

Edit [main_gui.py](main_gui.py#L217):
```python
ctk.set_appearance_mode("dark")  # or "light"
ctk.set_default_color_theme("blue")  # or "green", "dark-blue"
```

## Security

- `.env` file contains sensitive credentials
- Never commit `.env` to git (already in `.gitignore`)
- Device token is unique and secure
- Only registered devices can access your system

## Support

For issues:
1. Check this README
2. Review `agent.py` and `device_register.py`
3. Check Firebase console for device registration
4. Verify mobile app shows the device

---

**Note**: This GUI does **not** modify `agent.py` or `device_register.py`. It imports and uses their functions while providing a modern interface.
