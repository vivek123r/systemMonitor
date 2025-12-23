# 🎯 YOUR TODO - Complete These Steps

## 📋 Before You Can Run the App

### 1️⃣ Create Firebase Project (5 minutes)
**Action Required:**
1. Go to https://console.firebase.google.com/
2. Click "Add project" or "Create a project"
3. Name it (e.g., "System Monitor")
4. Follow the setup wizard

---

### 2️⃣ Enable Firebase Services (5 minutes)
**Action Required:**

**A. Enable Authentication:**
1. In Firebase Console, click "Authentication"
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Click "Email/Password"
5. Enable it and Save

**B. Enable Firestore:**
1. In Firebase Console, click "Firestore Database"
2. Click "Create database"
3. Start in "production mode"
4. Choose a location (closest to you)

---

### 3️⃣ Download Service Account Key (2 minutes)
**Action Required:**
1. In Firebase Console, click ⚙️ (Settings) > "Project settings"
2. Go to "Service accounts" tab
3. Click "Generate new private key"
4. Save the JSON file
5. **Rename it to:** `firebase-service-account.json`
6. **Move it to:** `c:\Users\vivek\projects\systemMonitor\`

---

### 4️⃣ Get Firebase Web Config (3 minutes)
**Action Required:**
1. In Firebase Console, click ⚙️ (Settings) > "Project settings"
2. Scroll down to "Your apps"
3. Click the **Web** icon (</>) to add a web app
4. Register the app (name it anything)
5. Copy the configuration values

You'll get something like:
```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:abcdef"
};
```

**Now open:** `c:\Users\vivek\projects\systemMonitor\systemmonitor\lib\main.dart`

**Replace lines 9-16** with your actual values:
```dart
const firebaseConfig = {
  'apiKey': 'YOUR_ACTUAL_API_KEY',              // ← Replace
  'appId': 'YOUR_ACTUAL_APP_ID',                // ← Replace
  'messagingSenderId': 'YOUR_ACTUAL_SENDER_ID', // ← Replace
  'projectId': 'YOUR_ACTUAL_PROJECT_ID',        // ← Replace
};
```

---

### 5️⃣ Install Python Dependencies (1 minute)
**Action Required:**
```powershell
cd c:\Users\vivek\projects\systemMonitor
pip install -r requirements.txt
```

---

### 6️⃣ Install Flutter Dependencies (1 minute)
**Action Required:**
```powershell
cd c:\Users\vivek\projects\systemMonitor\systemmonitor
flutter pub get
```

---

### 7️⃣ Create Your First User Account (2 minutes)
**Action Required:**

**Option A: From Mobile App (Recommended)**
1. Run the Flutter app: `flutter run`
2. Click "Sign Up" 
3. Enter email and password
4. Sign up
5. Copy your User ID (will add option to see this)

**Option B: From Firebase Console**
1. Go to Authentication > Users
2. Click "Add user"
3. Enter email and password
4. Copy the "User UID"

---

### 8️⃣ Register Your PC (1 minute)
**Action Required:**
```powershell
cd c:\Users\vivek\projects\systemMonitor
python device_register.py
```

**When prompted:**
- Enter your User ID (from step 7)
- Enter a device name (e.g., "My Laptop")

This creates a `.env` file with your device credentials.

---

### 9️⃣ Start the Agent (Test It!)
**Action Required:**
```powershell
python agent.py
```

**Expected output:**
```
✓ Sent Data:
  OS: Windows 10 | Uptime: 5h
  CPU: 25% (8 cores @ 2400 MHz)
  RAM: 45% (7.2/16 GB)
  GPU: 15% (NVIDIA GeForce GTX...)
```

---

### 🔟 Run the Mobile App
**Action Required:**
```powershell
cd systemmonitor
flutter run
```

**In the app:**
1. Sign in with your email/password
2. Select your device from dropdown
3. Try sending a command!

---

## ✅ Verification Checklist

After completing all steps, verify:

- [ ] `firebase-service-account.json` exists in project root
- [ ] Firebase config updated in `lib/main.dart`
- [ ] `.env` file exists with DEVICE_ID, USER_ID, DEVICE_TOKEN
- [ ] `pip install -r requirements.txt` completed
- [ ] `flutter pub get` completed
- [ ] Can run `python agent.py` without errors
- [ ] Can sign in to mobile app
- [ ] Device appears in mobile app dropdown
- [ ] Can send commands from mobile to PC

---

## 🆘 If Something Goes Wrong

### Agent won't start
- Check: `firebase-service-account.json` exists
- Check: `.env` file exists
- Run: `python device_register.py` again

### Mobile app won't login
- Check: Firebase config in `lib/main.dart` is correct
- Check: Email/Password is enabled in Firebase Console
- Check: Internet connection

### Device doesn't appear in app
- Check: Agent is running (`python agent.py`)
- Check: User ID matches in `.env` and mobile app
- Try: Refresh devices button in app

---

## 📚 Reference

- **Full Documentation:** `SETUP.md`
- **Quick Start:** `CHECKLIST.md`
- **Implementation Details:** `IMPLEMENTATION_SUMMARY.md`

---

**Estimated Total Time:** 20-30 minutes for first-time setup

**After Setup:** Just run `python agent.py` to start monitoring!
