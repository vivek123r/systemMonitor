# Firebase Configuration
# SETUP INSTRUCTIONS:
# 1. Go to Firebase Console: https://console.firebase.google.com/
# 2. Create a new project (or use existing)
# 3. Go to Project Settings > Service Accounts
# 4. Click "Generate new private key" and download the JSON file
# 5. Save it as 'firebase-service-account.json' in this directory
# 6. Enable Firebase Authentication (Email/Password) in Firebase Console

import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase with service account credentials"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
        return True
    except ValueError:
        # Not initialized, so initialize it
        try:
            cred_path = os.path.join(os.path.dirname(__file__), 'firebase-service-account.json')
            if not os.path.exists(cred_path):
                print("⚠️ WARNING: firebase-service-account.json not found!")
                print("Please download from Firebase Console > Project Settings > Service Accounts")
                return False
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {e}")
            return False

def verify_token(id_token):
    """Verify Firebase ID token and return user info"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return None

def get_firestore_db():
    """Get Firestore database instance"""
    return firestore.client()

# Initialize on import
initialize_firebase()
