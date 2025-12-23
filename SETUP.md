# System Monitor with Firebase Authentication

A secure system monitoring app with Firebase authentication. Monitor and control your PC remotely from your mobile device.

## 🔐 Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Agent     │────▶│  REST API    │────▶│   Mobile    │
│  (Your PC)  │     │  (Vercel)    │     │    App      │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Firebase   │
                    │ (Auth + DB)  │
                    └──────────────┘
```

## 🚀 Setup Instructions

### Step 1: Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (or use existing)
3. Enable **Authentication**:
   - Go to Authentication > Sign-in method
   - Enable "Email/Password"
4. Enable **Firestore Database**:
   - Go to Firestore Database
   - Create database (start in production mode)
5. Get Service Account Key:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save as `firebase-service-account.json` in project root
6. Get Web App Config:
   - Go to Project Settings > Your apps > Web app
   - Copy the config values

### Step 2: Backend Setup (Python)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Firebase
# 1. Place firebase-service-account.json in project root
# 2. Copy env.example to .env
cp env.example .env
```

### Step 3: Register Your PC

```bash
# Run device registration script
python device_register.py

# Follow prompts:
# 1. Enter your Firebase User ID (get from mobile app or Firebase Console)
# 2. Enter a name for your PC (e.g., "My Laptop")
# 
# This creates a .env file with:
# - DEVICE_ID
# - USER_ID  
# - DEVICE_TOKEN
```

### Step 4: Start the Agent

```bash
# Run the monitoring agent
python agent.py

# The agent will:
# ✓ Load credentials from .env
# ✓ Authenticate with Firebase
# ✓ Send system metrics every 2 seconds
# ✓ Listen for remote commands
```

### Step 5: Flutter Mobile App Setup

```bash
cd systemmonitor

# Update Firebase config in lib/main.dart
# Replace firebaseConfig with your values from Firebase Console

# Install dependencies
flutter pub get

# Run the app
flutter run
```

### Step 6: Mobile App Usage

1. **Sign Up**: Create an account with email/password
2. **View Devices**: See all PCs registered under your account
3. **Select Device**: Choose which PC to monitor/control
4. **Send Commands**: Control your PC remotely

## 📱 Features

### Monitoring
- ✅ CPU usage (total & per-core)
- ✅ RAM usage & details
- ✅ GPU usage
- ✅ Disk usage (all partitions)
- ✅ Network traffic
- ✅ Battery status (laptops)
- ✅ Running processes

### Remote Control
- ✅ Shutdown/Restart/Sleep/Logoff
- ✅ Power profile (High/Balanced/Power Saver)
- ✅ Brightness control
- ✅ Application control (open/close apps)
- ✅ Screenshot capture

### Security
- 🔐 Firebase Authentication
- 🔐 User-specific device ownership
- 🔐 Token-based API authentication
- 🔐 Device ID verification

## 🔒 Security Notes

**IMPORTANT**: 
- Never commit `.env` or `firebase-service-account.json` to git
- Keep your device tokens secure
- Each PC needs unique device credentials
- Only the device owner can send commands

## 📂 File Structure

```
systemMonitor/
├── agent.py                    # PC monitoring agent
├── server.py                   # REST API
├── firebase_config.py          # Firebase initialization
├── device_register.py          # Device registration script
├── requirements.txt            # Python dependencies
├── .env                        # Device credentials (DO NOT COMMIT)
├── firebase-service-account.json  # Firebase key (DO NOT COMMIT)
├── env.example                 # Example .env file
│
└── systemmonitor/              # Flutter mobile app
    ├── lib/
    │   ├── main.dart           # App entry point
    │   ├── login_page.dart     # Login/signup screen
    │   ├── auth_service.dart   # Firebase auth service
    │   └── remote_control_page.dart  # Device control UI
    └── pubspec.yaml            # Flutter dependencies
```

## 🛠️ API Endpoints

### Authentication Required (Headers)
```
X-User-ID: <firebase-user-id>
X-Device-ID: <device-id>
Authorization: Bearer <firebase-id-token>
```

### Endpoints
- `POST /api/update` - Send system stats (agent → server)
- `GET /api/status` - Get device stats (mobile → server)
- `GET /api/devices` - List all user devices (mobile → server)
- `GET /api/commands` - Get pending commands (agent → server)
- `POST /api/command?target_device_id=<id>` - Send command (mobile → server)
- `POST /api/command/ack/<id>` - Acknowledge command (agent → server)

## 🐛 Troubleshooting

### Agent can't connect
- Check `.env` file exists and has valid credentials
- Verify `firebase-service-account.json` is in project root
- Check internet connection

### Mobile app can't login
- Verify Firebase config in `main.dart` is correct
- Check Email/Password auth is enabled in Firebase Console
- Ensure app has internet connection

### Commands not working
- Verify device is online (check agent.py is running)
- Check device is selected in mobile app
- Verify user owns the device

## 📝 Adding New Devices

To add another PC:

1. Install Python dependencies on new PC
2. Copy `agent.py`, `server.py`, `firebase_config.py`, `firebase-service-account.json`
3. Run `python device_register.py` with **same User ID**
4. Run `python agent.py`
5. Device will appear in mobile app automatically

## 🔄 Demo Mode

For testing without Firebase:
- Agent uses `demo-user` and `demo-token` if no `.env` exists
- Server allows demo credentials for testing
- Not secure - only for development

## 📄 License

MIT License - Feel free to modify and use for your projects!
