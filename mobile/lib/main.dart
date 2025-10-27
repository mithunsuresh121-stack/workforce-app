import 'package:flutter/material.dart';
import 'package:workforce_app/src/app.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase
  await Firebase.initializeApp();

  // Initialize Firebase Messaging
  FirebaseMessaging messaging = FirebaseMessaging.instance;

  // Request permission for iOS
  NotificationSettings settings = await messaging.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false,
    provisional: false,
    sound: true,
  );

  print('User granted permission: ${settings.authorizationStatus}');

  // Get FCM token
  String? token = await messaging.getToken();
  print('FCM Token: $token');

  // Send FCM token to backend if user is logged in
  if (token != null) {
    try {
      final apiService = ApiService();
      final authToken = await apiService.getToken();
      if (authToken != null) {
        await apiService.updateFCMToken(token);
        print('FCM Token sent to backend');
      }
    } catch (e) {
      print('Error sending FCM token to backend: $e');
    }
  }

  // Handle foreground messages
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    print('Got a message whilst in the foreground!');
    print('Message data: ${message.data}');

    if (message.notification != null) {
      print('Message also contained a notification: ${message.notification}');
      // TODO: Show in-app notification using Flutter Local Notifications or similar
    }
  });

  // Handle token refresh
  FirebaseMessaging.instance.onTokenRefresh.listen((String token) async {
    print('FCM Token refreshed: $token');
    try {
      final apiService = ApiService();
      final authToken = await apiService.getToken();
      if (authToken != null) {
        await apiService.updateFCMToken(token);
        print('Refreshed FCM Token sent to backend');
      }
    } catch (e) {
      print('Error sending refreshed FCM token to backend: $e');
    }
  });

  // Handle background messages
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

  try {
    runApp(
      const ProviderScope(
        child: WorkforceApp(),
      ),
    );
  } catch (e) {
    // Removed print statement
  }
}

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('Handling a background message: ${message.messageId}');
}
