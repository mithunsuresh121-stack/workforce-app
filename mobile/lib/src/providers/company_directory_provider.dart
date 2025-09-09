import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';

class CompanyUser {
  final int id;
  final String email;
  final String? fullName;
  final String role;
  final int? companyId;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final EmployeeProfile? employeeProfile;

  CompanyUser({
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

  factory CompanyUser.fromJson(Map<String, dynamic> json) {
    return CompanyUser(
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

class CompanyDirectoryState {
  final List<CompanyUser> users;
  final List<String> departments;
  final List<String> positions;
  final bool isLoading;
  final String? error;
  final String? selectedDepartment;
  final String? selectedPosition;
  final String sortBy;
  final String sortOrder;

  CompanyDirectoryState({
    this.users = const [],
    this.departments = const [],
    this.positions = const [],
    this.isLoading = false,
    this.error,
    this.selectedDepartment,
    this.selectedPosition,
    this.sortBy = 'full_name',
    this.sortOrder = 'asc',
  });

  CompanyDirectoryState copyWith({
    List<CompanyUser>? users,
    List<String>? departments,
    List<String>? positions,
    bool? isLoading,
    String? error,
    String? selectedDepartment,
    String? selectedPosition,
    String? sortBy,
    String? sortOrder,
  }) {
    return CompanyDirectoryState(
      users: users ?? this.users,
      departments: departments ?? this.departments,
      positions: positions ?? this.positions,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      selectedDepartment: selectedDepartment ?? this.selectedDepartment,
      selectedPosition: selectedPosition ?? this.selectedPosition,
      sortBy: sortBy ?? this.sortBy,
      sortOrder: sortOrder ?? this.sortOrder,
    );
  }
}

class CompanyDirectoryNotifier extends StateNotifier<CompanyDirectoryState> {
  final ApiService _apiService;
  final int companyId;

  CompanyDirectoryNotifier(this._apiService, this.companyId) : super(CompanyDirectoryState());

  Future<void> fetchUsers() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.getCompanyUsers(
        companyId,
        department: state.selectedDepartment,
        position: state.selectedPosition,
        sortBy: state.sortBy,
        sortOrder: state.sortOrder,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final users = (data['users'] as List)
            .map((userJson) => CompanyUser.fromJson(userJson))
            .toList();

        state = state.copyWith(
          users: users,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Failed to load company users',
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> fetchDepartments() async {
    try {
      final response = await _apiService.getCompanyDepartments(companyId);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final departments = List<String>.from(data['departments']);
        state = state.copyWith(departments: departments);
      }
    } catch (e) {
      // Handle error silently for departments
    }
  }

  Future<void> fetchPositions() async {
    try {
      final response = await _apiService.getCompanyPositions(companyId);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final positions = List<String>.from(data['positions']);
        state = state.copyWith(positions: positions);
      }
    } catch (e) {
      // Handle error silently for positions
    }
  }

  Future<void> initialize() async {
    await Future.wait([
      fetchUsers(),
      fetchDepartments(),
      fetchPositions(),
    ]);
  }

  void setFilters({
    String? department,
    String? position,
  }) {
    state = state.copyWith(
      selectedDepartment: department,
      selectedPosition: position,
    );
    fetchUsers();
  }

  void setSorting(String sortBy, String sortOrder) {
    state = state.copyWith(
      sortBy: sortBy,
      sortOrder: sortOrder,
    );
    fetchUsers();
  }

  void clearFilters() {
    state = state.copyWith(
      selectedDepartment: null,
      selectedPosition: null,
    );
    fetchUsers();
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

final companyDirectoryProvider = StateNotifierProvider.family<CompanyDirectoryNotifier, CompanyDirectoryState, int>((ref, companyId) {
  final apiService = ApiService();
  return CompanyDirectoryNotifier(apiService, companyId);
});
