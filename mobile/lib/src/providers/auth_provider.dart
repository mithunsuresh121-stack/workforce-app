import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';

class AuthState {
  final bool isAuthenticated;
  final String? token;
  final String? email;
  final String? role;
  final int? companyId;
  final List<Map<String, dynamic>>? userCompanies;
  final bool isLoading;
  final String? error;

  AuthState({
    this.isAuthenticated = false,
    this.token,
    this.email,
    this.role,
    this.companyId,
    this.userCompanies,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    String? token,
    String? email,
    String? role,
    int? companyId,
    List<Map<String, dynamic>>? userCompanies,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      token: token ?? this.token,
      email: email ?? this.email,
      role: role ?? this.role,
      companyId: companyId ?? this.companyId,
      userCompanies: userCompanies ?? this.userCompanies,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiService _apiService;

  AuthNotifier(this._apiService) : super(AuthState());

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final data = await _apiService.login(email, password);
      final token = data['access_token'];

      // Decode JWT to get user info
      final decodedToken = JwtDecoder.decode(token);
      final companyId = decodedToken['company_id'];
      final role = decodedToken['role'];

      // Get user's companies
      final companiesResponse = await _apiService.getUserCompanies();
      final companies = json.decode(companiesResponse.body) as List<dynamic>;
      final userCompanies = companies.map((c) => c as Map<String, dynamic>).toList();

      state = state.copyWith(
        isAuthenticated: true,
        token: token,
        email: email,
        role: role,
        companyId: companyId,
        userCompanies: userCompanies,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> signup(String email, String password, String fullName) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _apiService.signup(email, password, fullName);
      if (response.statusCode == 201) {
        // After successful signup, get user's companies (should be empty)
        final companiesResponse = await _apiService.getUserCompanies();
        final companies = json.decode(companiesResponse.body) as List<dynamic>;
        final userCompanies = companies.map((c) => c as Map<String, dynamic>).toList();

        state = state.copyWith(
          userCompanies: userCompanies,
          isLoading: false,
          error: null,
        );
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'Signup failed');
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> logout() async {
    await _apiService.deleteToken();
    state = AuthState();
  }

  Future<void> checkAuthStatus() async {
    final token = await _apiService.getToken();
    if (token != null) {
      try {
        // Decode JWT to get user info
        final decodedToken = JwtDecoder.decode(token);
        final companyId = decodedToken['company_id'];
        final role = decodedToken['role'];
        final email = decodedToken['sub'];

        // Get user's companies
        final companiesResponse = await _apiService.getUserCompanies();
        final companies = json.decode(companiesResponse.body) as List<dynamic>;
        final userCompanies = companies.map((c) => c as Map<String, dynamic>).toList();

        state = state.copyWith(
          isAuthenticated: true,
          token: token,
          email: email,
          role: role,
          companyId: companyId,
          userCompanies: userCompanies,
          isLoading: false,
        );
      } catch (e) {
        // Token invalid, clear it
        await _apiService.deleteToken();
        state = state.copyWith(isLoading: false);
      }
    } else {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> switchCompany(int companyId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // Update stored company ID
      const FlutterSecureStorage storage = FlutterSecureStorage();
      await storage.write(key: 'current_company_id', value: companyId.toString());

      state = state.copyWith(
        companyId: companyId,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final apiService = ApiService();
  return AuthNotifier(apiService);
});
