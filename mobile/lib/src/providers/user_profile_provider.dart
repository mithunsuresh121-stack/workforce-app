import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';

class UserProfile {
  final int id;
  final String email;
  final String? fullName;
  final String role;
  final int? companyId;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final EmployeeProfile? employeeProfile;

  UserProfile({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    required this.companyId,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.employeeProfile,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      email: json['email'],
      fullName: json['full_name'],
      role: json['role'],
      companyId: json['company_id'],
      isActive: json['is_active'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      employeeProfile: json['employee_profile'] != null
          ? EmployeeProfile.fromJson(json['employee_profile'])
          : null,
    );
  }
}

class EmployeeProfile {
  final int id;
  final int userId;
  final int companyId;
  final String? department;
  final String? position;
  final String? phone;
  final DateTime? hireDate;
  final int? managerId;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  EmployeeProfile({
    required this.id,
    required this.userId,
    required this.companyId,
    this.department,
    this.position,
    this.phone,
    this.hireDate,
    this.managerId,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  factory EmployeeProfile.fromJson(Map<String, dynamic> json) {
    return EmployeeProfile(
      id: json['id'],
      userId: json['user_id'],
      companyId: json['company_id'],
      department: json['department'],
      position: json['position'],
      phone: json['phone'],
      hireDate: json['hire_date'] != null ? DateTime.parse(json['hire_date']) : null,
      managerId: json['manager_id'],
      isActive: json['is_active'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}

class UserProfileState {
  final UserProfile? profile;
  final bool isLoading;
  final String? error;

  UserProfileState({
    this.profile,
    this.isLoading = false,
    this.error,
  });

  UserProfileState copyWith({
    UserProfile? profile,
    bool? isLoading,
    String? error,
  }) {
    return UserProfileState(
      profile: profile ?? this.profile,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class UserProfileNotifier extends StateNotifier<UserProfileState> {
  final ApiService _apiService;

  UserProfileNotifier(this._apiService) : super(UserProfileState());

  Future<void> fetchUserProfile() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.getCurrentUserFullProfile();
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final profile = UserProfile.fromJson(data['user']);
        final employeeProfile = data['employee_profile'] != null
            ? EmployeeProfile.fromJson(data['employee_profile'])
            : null;

        final fullProfile = UserProfile(
          id: profile.id,
          email: profile.email,
          fullName: profile.fullName,
          role: profile.role,
          companyId: profile.companyId,
          isActive: profile.isActive,
          createdAt: profile.createdAt,
          updatedAt: profile.updatedAt,
          employeeProfile: employeeProfile,
        );

        state = state.copyWith(profile: fullProfile, isLoading: false);
      } else {
        state = state.copyWith(isLoading: false, error: 'Failed to load user profile');
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> updateUserProfile(Map<String, dynamic> updateData) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.updateCurrentUserProfile(updateData);
      if (response.statusCode == 200) {
        await fetchUserProfile(); // Refresh the profile after update
      } else {
        final errorData = json.decode(response.body);
        state = state.copyWith(isLoading: false, error: errorData['detail'] ?? 'Failed to update profile');
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

final userProfileProvider = StateNotifierProvider<UserProfileNotifier, UserProfileState>((ref) {
  final apiService = ApiService();
  return UserProfileNotifier(apiService);
});
