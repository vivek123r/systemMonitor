# 🖥️ System Monitor

A comprehensive, cross-platform system monitoring and remote control application that enables real-time PC performance tracking and secure remote management from mobile devices.

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Flutter](https://img.shields.io/badge/Flutter-Latest-blue?logo=flutter)](https://flutter.dev)
[![Firebase](https://img.shields.io/badge/Firebase-Enabled-yellow?logo=firebase)](https://firebase.google.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## Overview

System Monitor is a full-stack, production-ready application that allows users to:
- **Monitor** their PC's performance metrics in real-time (CPU, RAM, GPU, Disk, Network, Battery)
- **Control** their PC remotely (Power, Brightness, Volume, Quick Actions)
- **Manage** devices securely with multi-user support
- **Share** files across devices on the same network

The application consists of three main components:
- **Windows Desktop App** (Python + CustomTkinter)
- **Flutter Mobile App** (iOS, Android, Web, Linux, macOS, Windows)
- **Cloud Backend** (FastAPI + Firebase + Vercel)

---

## ✨ Features

### 🖥️ Desktop Application (Windows)

| Feature | Details |
|---------|---------|
| **Real-time Monitoring** | CPU, RAM, GPU, Disk, Network, Battery metrics |
| **System Control** | Power (Shutdown/Restart/Sleep), Brightness, Volume |
| **Device Registration** | Secure Firebase-based setup |
| **Command Logging** | Timestamped history of all operations |
| **Local File Sharing** | LAN file transfer with QR code connection |
| **Modern UI** | Dark theme with responsive design |
| **Background Monitoring** | Continuous agent service for data collection |

### 📱 Mobile Application (Flutter)

| Feature | Platform Support |
|---------|------------------|
| **Secure Login** | Email/password with Firebase Auth |
| **Device Management** | View and control registered devices |
| **Remote Commands** | Real-time command execution |
| **Live Metrics** | Monitor PC metrics on mobile |
| **File Sharing** | Receive files from PC over LAN |
| **Cross-Platform** | iOS, Android, Web, Linux, macOS, Windows |

### ☁️ Backend API

| Feature | Technology |
|---------|-----------|
| **REST Endpoints** | FastAPI with secure authentication |
| **Real-time Queue** | Firestore command management |
| **Multi-user Support** | Device ownership and access control |
| **Cloud Deployment** | Vercel serverless infrastructure |

---

## 🛠️ Tech Stack

### Backend & Services
| Technology | Purpose |
|------------|---------|
| **Python 3** | Core backend language |
| **FastAPI** | REST API framework with auto-documentation |
| **Uvicorn** | ASGI server for FastAPI |
| **Firebase Admin SDK** | Authentication & Firestore database |
| **Pydantic** | Data validation and serialization |
| **Requests** | HTTP client for API calls |

### Desktop Application
| Technology | Purpose |
|------------|---------|
| **CustomTkinter** | Modern GUI framework |
| **Psutil** | System metrics collection |
| **GPUtil** | GPU monitoring |
| **Pillow (PIL)** | Image processing |
| **QRCode** | QR code generation |
| **Flask** | Local file server |
| **Screen-brightness-control** | Display brightness management |

### Mobile Application
| Technology | Purpose |
|------------|---------|
| **Flutter/Dart** | Cross-platform mobile framework |
| **Firebase SDK** | Authentication & database integration |
| **Mobile Scanner** | QR code scanning |
| **File Picker** | File selection UI |
| **Shared Preferences** | Local data persistence |

### Cloud Infrastructure
| Service | Usage |
|---------|-------|
| **Firebase** | Auth, Firestore DB, Hosting |
| **Vercel** | API deployment & serverless functions |
| **Google Cloud** | Backend infrastructure |

---

## 📦 Installation

### Prerequisites
- **Windows 10/11** (Desktop app)
- **Python 3.8+**
- **Flutter** (for mobile app development)
- **Firebase Project** (for backend services)
- **Git**

### Backend Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/systemMonitor.git
cd systemMonitor
```

2. **Create Virtual Environment**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/macOS
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Firebase**
```bash
# Copy the example environment file
cp env.example .env

# Add your Firebase credentials to .env
# FIREBASE_API_KEY=your_key
# FIREBASE_PROJECT_ID=your_project
# etc.
```

5. **Set Up Firebase Service Account**
```bash
# Place your firebase-service-account.json in the project root
# This file contains your Firebase Admin SDK credentials
```

### Mobile App Setup

1. **Navigate to Flutter App**
```bash
cd systemmonitor
```

2. **Get Flutter Dependencies**
```bash
flutter pub get
```

3. **Configure Firebase for Flutter**
   - Follow Flutter Firebase setup guide
   - Update `google-services.json` (Android)
   - Update `GoogleService-Info.plist` (iOS)

4. **Run on Emulator or Device**
```bash
flutter run
```

---

## 🚀 Quick Start

### 1. Register Your Device
```bash
python device_register.py
```
- Creates a unique device ID
- Registers with Firebase
- Generates credentials for the desktop app

### 2. Start the Monitoring Agent
```bash
python agent.py
```
- Collects system metrics every 2 seconds
- Publishes to Firebase Firestore
- Listens for remote commands

### 3. Launch Desktop GUI
```bash
python main_gui.py
```
- Opens the monitoring dashboard
- Shows real-time system metrics
- Allows device management and local file sharing

### 4. Connect Mobile App
- Install Flutter app on your mobile device
- Login with your Firebase credentials
- Your registered device appears automatically
- Send commands and monitor remotely

---

## 📁 Project Structure

```
systemMonitor/
├── 📄 main_gui.py              # Windows desktop GUI application
├── 📄 agent.py                 # Background monitoring service (runs continuously)
├── 📄 server.py                # FastAPI backend server
├── 📄 device_register.py       # Device registration utility
├── 📄 local_file_server.py     # LAN file sharing server
├── 📄 firebase_config.py       # Firebase configuration
├── 📄 firebase-service-account.json # Firebase credentials (not in git)
├── 📄 requirements.txt          # Python dependencies
├── 📄 env.example              # Environment variables template
├── 📄 vercel.json              # Vercel deployment config
│
├── 📁 systemmonitor/           # Flutter mobile application
│   ├── 📁 lib/
│   │   ├── 📄 main.dart
│   │   ├── 📄 login_page.dart
│   │   ├── 📄 remote_control_page.dart
│   │   ├── 📄 local_file_share.dart
│   │   └── 📄 auth_service.dart
│   ├── 📁 android/             # Android build configuration
│   ├── 📁 ios/                 # iOS build configuration
│   ├── 📁 web/                 # Web build files
│   ├── 📁 linux/               # Linux build configuration
│   ├── 📁 macos/               # macOS build configuration
│   ├── 📁 windows/             # Windows build configuration
│   ├── 📁 test/                # Widget tests
│   └── 📄 pubspec.yaml         # Flutter dependencies
│
├── 📁 api/                     # Vercel serverless API
│   └── 📄 index.py
│
└── 📄 README.md                # This file
```

---

## 🏗️ Architecture

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Devices                         │
│  ┌──────────────────┐          ┌────────────────────┐  │
│  │  Desktop App     │          │  Mobile App        │  │
│  │  (Windows GUI)   │◄────────►│  (Flutter)         │  │
│  └──────────────────┘          └────────────────────┘  │
│           │                              │              │
│           │ REST API                     │ REST API     │
│           │                              │              │
└───────────┼──────────────────────────────┼──────────────┘
            │                              │
            │                              │
      ┌─────▼──────────────────────────────▼─────┐
      │                                           │
      │     FastAPI Backend (server.py)          │
      │     ├─ Authentication Endpoints          │
      │     ├─ Device Management Endpoints       │
      │     ├─ Metrics Collection Endpoints      │
      │     └─ Command Queue Endpoints           │
      │                                           │
      └──────────────────┬──────────────────────┘
                         │
                ┌────────▼─────────┐
                │                  │
      ┌─────────▼────────┐ ┌──────▼──────────┐
      │ Firebase Auth    │ │ Firestore DB   │
      │ (User Login)     │ │ (Data Storage) │
      └──────────────────┘ └────────────────┘
```

### Component Interaction

| Component | Role | Communication |
|-----------|------|---|
| **Desktop App (GUI)** | User interface & local control | HTTP REST API → Backend |
| **Monitoring Agent** | Collects metrics continuously | Publishes to Firestore |
| **FastAPI Server** | API gateway & business logic | HTTP endpoints |
| **Firebase Auth** | User authentication | OAuth tokens |
| **Firestore Database** | Central data storage | Real-time listeners |
| **Mobile App** | Remote monitoring & control | HTTP REST API → Backend |

---

## 💻 Usage

### Desktop Application

1. **Launch the GUI**
```bash
python main_gui.py
```

2. **View System Metrics**
   - CPU usage (real-time percentage)
   - RAM usage (GB and percentage)
   - GPU usage and temperature
   - Disk usage across all partitions
   - Network activity (upload/download)
   - Battery status

3. **Remote Control**
   - **Power Controls**: Shutdown, Restart, Sleep, Logoff, Lock
   - **Brightness**: Adjust display brightness (0-100%)
   - **Volume**: Mute/unmute and adjust volume level
   - **Quick Actions**: Screenshot, Open Explorer, Open Browser

4. **File Sharing**
   - Share files over LAN with QR code
   - Mobile app scans QR to connect
   - Receive shared files from mobile

5. **View Command Log**
   - Timestamped history of all executed commands
   - Track remote control actions

### Mobile Application

1. **Register Account**
   - Sign up with email and password
   - Firebase authentication handles credentials

2. **Login**
   - Enter email and password
   - Automatic device discovery from your account

3. **Monitor Your PC**
   - View real-time system metrics
   - Refresh data with pull-to-refresh
   - Monitor historical data

4. **Send Remote Commands**
   - Tap command buttons for instant execution
   - Confirm critical actions (shutdown, restart)
   - View command response status

5. **Receive Files**
   - Tap "File Sharing" in mobile app
   - Scan QR code from desktop GUI
   - Receive files from desktop app

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```env
# Firebase Configuration
FIREBASE_API_KEY=your_api_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your_project.firebaseio.com
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id

# Backend Configuration
BACKEND_URL=http://localhost:8000
VERCEL_API_URL=https://your_vercel_deployment.vercel.app

# Server Configuration
SERVER_PORT=8000
SERVER_HOST=0.0.0.0
DEBUG_MODE=False

# Agent Configuration
MONITORING_INTERVAL=2
LOG_LEVEL=INFO
```

### Firebase Security Rules

Database rules are configured in `database.rules.json` to ensure:
- Users can only access their own devices
- Device metrics are properly isolated
- Command queues are secure and tamper-proof

---

## 📚 API Documentation

### Authentication

**POST** `/api/auth/login`
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": "user_123",
  "device_id": "device_456"
}
```

### Metrics Endpoints

**GET** `/api/metrics/latest/{device_id}`
- Retrieve latest system metrics

**GET** `/api/metrics/history/{device_id}?limit=100`
- Get historical metrics data

### Command Endpoints

**POST** `/api/commands/execute`
```json
{
  "device_id": "device_123",
  "command": "shutdown",
  "parameters": {}
}
```

**GET** `/api/commands/status/{command_id}`
- Check command execution status

### Device Endpoints

**GET** `/api/devices`
- List all registered devices

**POST** `/api/devices/register`
- Register a new device

**DELETE** `/api/devices/{device_id}`
- Unregister a device

---

## 🔐 Security

### Authentication & Authorization
- **Firebase Auth**: Email/password authentication with Firebase
- **Bearer Tokens**: JWT tokens for API requests
- **Device Verification**: Each device has unique ID and credentials
- **User Isolation**: Users can only access their own devices

### Data Protection
- **HTTPS/TLS**: Encrypted data transmission
- **Environment Variables**: Sensitive data in `.env` file (not in git)
- **Firebase Rules**: Database security rules enforce access control
- **Service Account**: Firebase admin credentials stored securely

### Best Practices
- Never commit `.env` file or `firebase-service-account.json`
- Use `.gitignore` to exclude sensitive files
- Rotate Firebase keys regularly
- Enable 2FA on Firebase console

---

## 🤝 Contributing

We welcome contributions! To get started:

1. **Fork the Repository**
```bash
git clone https://github.com/yourusername/systemMonitor.git
cd systemMonitor
```

2. **Create a Feature Branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make Your Changes**
   - Follow PEP 8 style guide for Python
   - Add comments for complex logic
   - Update documentation as needed

4. **Commit Your Changes**
```bash
git commit -m 'Add amazing feature'
```

5. **Push to Branch**
```bash
git push origin feature/amazing-feature
```

6. **Open a Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all tests pass

### Development Setup

```bash
# Install development dependencies
pip install pytest flake8 black

# Format code
black .

# Lint code
flake8 .

# Run tests
pytest tests/
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Vivek Kumar**

- GitHub: [@yourusername](https://github.com/yourusername)
- Portfolio: [Your Portfolio](https://yourportfolio.com)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Firebase for authentication and database services
- Flutter team for the amazing mobile framework
- FastAPI for the modern Python web framework
- The open-source community for incredible libraries

---

## 📞 Support

For questions or issues:
- **Issues**: Open an issue on [GitHub Issues](https://github.com/yourusername/systemMonitor/issues)
- **Discussions**: Join our community discussions
- **Email**: your.email@example.com

---

## 🗺️ Roadmap

- [ ] Add real-time alerts for high CPU/RAM usage
- [ ] Implement scheduled maintenance tasks
- [ ] Add performance history charts
- [ ] Implement device groups and automation
- [ ] Add SMS/Email notifications
- [ ] Create desktop app for macOS and Linux
- [ ] Implement end-to-end encrypted messaging
- [ ] Add support for multiple monitor setup

---

<div align="center">

**[⬆ Back to Top](#system-monitor)**

Made with ❤️ by [Vivek Kumar]

</div>
