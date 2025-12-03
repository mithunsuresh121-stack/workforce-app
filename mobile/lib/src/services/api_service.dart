import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

class ApiService {
  static const String baseUrl = 'https://api.workforce-app.com';
  static const String wsUrl = 'wss://api.workforce-app.com/ws/notifications';
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  late FirebaseMessaging _firebaseMessaging;
  final Connectivity _connectivity = Connectivity();

  Future<String?> getToken() async {
    return await _secureStorage.read(key: 'auth_token');
  }

  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: 'refresh_token');
  }

  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: 'auth_token', value: token);
  }

  Future<void> saveRefreshToken(String refreshToken) async {
    await _secureStorage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<void> deleteToken() async {
    await _secureStorage.delete(key: 'auth_token');
  }

  Future<void> deleteRefreshToken() async {
    await _secureStorage.delete(key: 'refresh_token');
  }

  Future<bool> isConnected() async {
    var connectivityResult = await _connectivity.checkConnectivity();
    return connectivityResult != ConnectivityResult.none;
  }

  Future<Map<String, String>> _getHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': token != null ? 'Bearer $token' : '',
      'X-FCM-Token': await _getFCMToken() ?? '',
    };
  }

  Future<String?> _getFCMToken() async {
    try {
      await Firebase.initializeApp();
      _firebaseMessaging = FirebaseMessaging.instance;
      return await _firebaseMessaging.getToken();
    } catch (e) {
      print('Error getting FCM token: $e');
      return null;
    }
  }

  Future<http.Response> get(String endpoint) async {
    if (!await isConnected()) {
      throw Exception('No internet connection');
    }
    final headers = await _getHeaders();
    return await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
    );
  }

  Future<http.Response> post(String endpoint, dynamic data) async {
    if (!await isConnected()) {
      throw Exception('No internet connection');
    }
    final headers = await _getHeaders();
    return await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: json.encode(data),
    );
  }

  Future<http.Response> put(String endpoint, dynamic data) async {
    if (!await isConnected()) {
      throw Exception('No internet connection');
    }
    final headers = await _getHeaders();
    return await http.put(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: json.encode(data),
    );
  }

  Future<http.Response> delete(String endpoint) async {
    if (!await isConnected()) {
      throw Exception('No internet connection');
    }
    final headers = await _getHeaders();
    return await http.delete(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
    );
  }

  // Auth specific methods
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await post('/auth/login', {
      'email': email,
      'password': password,
    });

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final accessToken = data['access_token'];
      final refreshToken = data['refresh_token'];

      await saveToken(accessToken);
      await saveRefreshToken(refreshToken);

      return data;
    } else {
      throw Exception('Login failed: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> refreshToken() async {
    final refreshToken = await getRefreshToken();
    if (refreshToken == null) {
      throw Exception('No refresh token available');
    }

    final response = await post('/auth/refresh', {
      'refresh_token': refreshToken,
    });

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final newAccessToken = data['access_token'];
      final newRefreshToken = data['refresh_token'];

      await saveToken(newAccessToken);
      await saveRefreshToken(newRefreshToken);

      return data;
    } else {
      // If refresh fails, clear tokens
      await deleteToken();
      await deleteRefreshToken();
      throw Exception('Token refresh failed: ${response.body}');
    }
  }

  Future<http.Response> signup(String email, String password, String fullName) async {
    return await post('/auth/signup', {
      'email': email,
      'password': password,
      'full_name': fullName,
    });
  }

  // Task specific methods
  Future<http.Response> getTasks() async {
    return await get('/tasks/');
  }

  Future<http.Response> createTask(Map<String, dynamic> taskData) async {
    return await post('/tasks/', taskData);
  }

  Future<http.Response> updateTask(int taskId, Map<String, dynamic> taskData) async {
    return await put('/tasks/$taskId', taskData);
  }

  Future<http.Response> deleteTask(int taskId) async {
    return await delete('/tasks/$taskId');
  }

  // Company specific methods
  Future<http.Response> getCompanies() async {
    return await get('/companies/');
  }

  Future<http.Response> getCompany(int companyId) async {
    return await get('/companies/$companyId');
  }

  // Employee specific methods
  Future<http.Response> getEmployees() async {
    return await get('/employees/');
  }

  Future<http.Response> getEmployee(int userId) async {
    return await get('/employees/$userId');
  }

  Future<http.Response> createEmployee(Map<String, dynamic> employeeData) async {
    return await post('/employees/', employeeData);
  }

  Future<http.Response> updateEmployee(int userId, Map<String, dynamic> employeeData) async {
    return await put('/employees/$userId', employeeData);
  }

  Future<http.Response> deleteEmployee(int userId) async {
    return await delete('/employees/$userId');
  }

  // Leave specific methods
  Future<http.Response> getLeaves() async {
    return await get('/leaves/');
  }

  Future<http.Response> getLeave(int leaveId) async {
    return await get('/leaves/$leaveId');
  }

  Future<http.Response> createLeave(Map<String, dynamic> leaveData) async {
    return await post('/leaves/', leaveData);
  }

  Future<http.Response> updateLeave(int leaveId, Map<String, dynamic> leaveData) async {
    return await put('/leaves/$leaveId', leaveData);
  }

  Future<http.Response> updateLeaveStatus(int leaveId, String status) async {
    return await put('/leaves/$leaveId/status', {'status': status});
  }

  Future<http.Response> deleteLeave(int leaveId) async {
    return await delete('/leaves/$leaveId');
  }

  // Shift specific methods
  Future<http.Response> getShifts() async {
    return await get('/shifts/');
  }

  Future<http.Response> getShift(int shiftId) async {
    return await get('/shifts/$shiftId');
  }

  Future<http.Response> createShift(Map<String, dynamic> shiftData) async {
    return await post('/shifts/', shiftData);
  }

  Future<http.Response> updateShift(int shiftId, Map<String, dynamic> shiftData) async {
    return await put('/shifts/$shiftId', shiftData);
  }

  Future<http.Response> updateShiftStatus(int shiftId, String status) async {
    return await put('/shifts/$shiftId/status', {'status': status});
  }

  Future<http.Response> deleteShift(int shiftId) async {
    return await delete('/shifts/$shiftId');
  }

  // User profile methods
  Future<http.Response> getCurrentUserProfile() async {
    return await get('/auth/me');
  }

  // Notification preferences methods
  Future<http.Response> getNotificationPreferences() async {
    return await get('/notification-preferences/');
  }

  Future<http.Response> createNotificationPreferences(Map<String, dynamic> preferences) async {
    return await post('/notification-preferences/', preferences);
  }

  Future<http.Response> updateNotificationPreferences(Map<String, dynamic> preferences) async {
    return await put('/notification-preferences/', preferences);
  }

  Future<http.Response> deleteNotificationPreferences() async {
    return await delete('/notification-preferences/');
  }

  // Notification methods
  Future<http.Response> getNotifications() async {
    return await get('/notifications/');
  }

  Future<http.Response> markNotificationAsRead(int notificationId) async {
    return await post('/notifications/mark-read/$notificationId', {});
  }

  // FCM Token management
  Future<http.Response> updateFCMToken(String fcmToken) async {
    return await post('/auth/update-fcm-token', {'fcm_token': fcmToken});
  }
}
