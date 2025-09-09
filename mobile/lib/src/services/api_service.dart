import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  Future<String?> getToken() async {
    return await _secureStorage.read(key: 'auth_token');
  }

  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: 'auth_token', value: token);
  }

  Future<void> deleteToken() async {
    await _secureStorage.delete(key: 'auth_token');
  }

  Future<Map<String, String>> _getHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': token != null ? 'Bearer $token' : '',
    };
  }

  Future<http.Response> get(String endpoint) async {
    final headers = await _getHeaders();
    return await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
    );
  }

  Future<http.Response> post(String endpoint, dynamic data) async {
    final headers = await _getHeaders();
    return await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: json.encode(data),
    );
  }

  Future<http.Response> put(String endpoint, dynamic data) async {
    final headers = await _getHeaders();
    return await http.put(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: json.encode(data),
    );
  }

  Future<http.Response> delete(String endpoint) async {
    final headers = await _getHeaders();
    return await http.delete(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
    );
  }

  // Auth specific methods
  Future<http.Response> login(String email, String password, int companyId) async {
    return await post('/auth/login', {
      'email': email,
      'password': password,
      'company_id': companyId,
    });
  }

  Future<http.Response> signup(String email, String password, String fullName, String role, int companyId) async {
    return await post('/auth/signup', {
      'email': email,
      'password': password,
      'full_name': fullName,
      'role': role,
      'company_id': companyId,
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

  Future<http.Response> getCompanyUsers(int companyId, {String? department, String? position, String? sortBy, String? sortOrder}) async {
    String url = '/companies/$companyId/users?';
    List<String> params = [];
    if (department != null) params.add('department=$department');
    if (position != null) params.add('position=$position');
    if (sortBy != null) params.add('sort_by=$sortBy');
    if (sortOrder != null) params.add('sort_order=$sortOrder');
    url += params.join('&');
    return await get(url);
  }

  Future<http.Response> getCompanyDepartments(int companyId) async {
    return await get('/companies/$companyId/departments');
  }

  Future<http.Response> getCompanyPositions(int companyId) async {
    return await get('/companies/$companyId/positions');
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

  Future<http.Response> getCurrentUserFullProfile() async {
    return await get('/auth/me/profile');
  }

  Future<http.Response> updateCurrentUserProfile(Map<String, dynamic> profileData) async {
    return await put('/auth/me/profile', profileData);
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
}
