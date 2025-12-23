# 🚀 Quick Start Checklist

## Prerequisites
- [ ] Python 3.7+ installed
- [ ] Flutter SDK installed  
- [ ] Firebase account created

## Firebase Setup (15 minutes)
- [ ] Create Firebase project at console.firebase.google.com
- [ ] Enable Authentication > Email/Password
- [ ] Enable Firestore Database
- [ ] Download service account JSON (Project Settings > Service Accounts)
- [ ] Save as `firebase-service-account.json` in project root
- [ ] Get Web App config (Project Settings > Your apps)
- [ ] Update `lib/main.dart` with Firebase config

## Backend Setup (5 minutes)
- [ ] `pip install -r requirements.txt`
- [ ] Place `firebase-service-account.json` in root
- [ ] Create first user account (can do from mobile app)
- [ ] Run `python device_register.py` to get device credentials
- [ ] Verify `.env` file created with credentials

## Mobile App Setup (10 minutes)
- [ ] `cd systemmonitor`
- [ ] Update Firebase config in `lib/main.dart`
- [ ] `flutter pub get`
- [ ] Connect device/emulator
- [ ] `flutter run`
- [ ] Create account / Sign in

## Testing (5 minutes)
- [ ] Run `python agent.py` on PC
- [ ] See "✓ Sent Data" messages
- [ ] Open mobile app
- [ ] See your device in dropdown
- [ ] Try sending a command (e.g., Power Profile)
- [ ] Verify command executes on PC

## Deploy (Optional)
- [ ] Deploy server.py to Vercel (already done if using vercel.app URL)
- [ ] Update API URLs in agent.py if needed
- [ ] Build Flutter app for production

## 🎉 You're Done!
Your system is now secure with:
- ✅ Firebase authentication
- ✅ User-specific devices
- ✅ Token-based API security
- ✅ Multi-device support

## Next Steps
- Add more PCs: Run device_register.py on each with same User ID
- Customize: Modify commands in agent.py
- Monitor: Check Firebase Console > Firestore for data
