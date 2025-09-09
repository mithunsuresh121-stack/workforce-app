import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';

class AuthState {
  final bool isAuthenticated;
  final String? token;
  final String? email;
  final String? role;
  final int? companyId;
  final bool isLoading;
  final String? error;

  AuthState({
    this.isAuthenticated = false,
    this.token,
    this.email,
    this.role,
    this.companyId,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    String? token,
    String? email,
    String? role,
    int? companyId,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      token: token ?? this.token,
      email: email ?? this.email,
      role: role ?? this.role,
      companyId: companyId ?? this.companyId,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiService _apiService;

  AuthNotifier(this._apiService) : super(AuthState());

  Future<void> login(String email, String password, int companyId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _apiService.login(email, password, companyId);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['access_token'];

        await _apiService.saveToken(token);

        // Fetch user profile to get role
        final profileResponse = await _apiService.getCurrentUserProfile();
        String? role;
        if (profileResponse.statusCode == 200) {
          final profileData = json.decode(profileResponse.body);
          role = profileData['role'];
        }

        state = state.copyWith(
          isAuthenticated: true,
          token: token,
          email: email,
          role: role,
          companyId: companyId,
          isLoading: false,
          error: null,
        );
      } else {
        final errorData = json.decode(response.body);
        state = state.copyWith(
          isLoading: false,
          error: errorData['detail'] ?? 'Login failed',
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Network error: ${e.toString()}',
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
      // TODO: Verify token validity with backend
      state = state.copyWith(
        isAuthenticated: true,
        token: token,
        isLoading: false,
      );
    } else {
      state = state.copyWith(isLoading: false);
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
