import 'package:firebase_auth/firebase_auth.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;

  // Get current user
  User? get currentUser => _auth.currentUser;

  // Get user ID
  String? get userId => _auth.currentUser?.uid;

  // Get ID token for API authentication
  Future<String?> getIdToken() async {
    return await _auth.currentUser?.getIdToken();
  }

  // Sign in with email and password
  Future<String?> signIn(String email, String password) async {
    try {
      await _auth.signInWithEmailAndPassword(email: email, password: password);
      return null; // Success
    } on FirebaseAuthException catch (e) {
      if (e.code == 'user-not-found') {
        return 'No user found with this email.';
      } else if (e.code == 'wrong-password') {
        return 'Wrong password provided.';
      }
      return e.message ?? 'An error occurred';
    }
  }

  // Register new user
  Future<String?> register(String email, String password) async {
    try {
      await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      return null; // Success
    } on FirebaseAuthException catch (e) {
      if (e.code == 'weak-password') {
        return 'The password is too weak.';
      } else if (e.code == 'email-already-in-use') {
        return 'An account already exists for this email.';
      }
      return e.message ?? 'An error occurred';
    }
  }

  // Sign out
  Future<void> signOut() async {
    await _auth.signOut();
  }

  // Reset password
  Future<String?> resetPassword(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email);
      return null; // Success
    } on FirebaseAuthException catch (e) {
      return e.message ?? 'An error occurred';
    }
  }

  // Listen to authentication state changes
  Stream<User?> get authStateChanges => _auth.authStateChanges();
}
