import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';

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
    );
  }
}

class EmployeesState {
  final List<EmployeeProfile> employees;
  final bool isLoading;
  final String? error;

  EmployeesState({
    this.employees = const [],
    this.isLoading = false,
    this.error,
  });

  EmployeesState copyWith({
    List<EmployeeProfile>? employees,
    bool? isLoading,
    String? error,
  }) {
    return EmployeesState(
      employees: employees ?? this.employees,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class EmployeesNotifier extends StateNotifier<EmployeesState> {
  final ApiService _apiService;

  EmployeesNotifier(this._apiService) : super(EmployeesState());

  Future<void> fetchEmployees() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.get('/employees/');
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        final employees = data.map((e) => EmployeeProfile.fromJson(e)).toList();
        state = state.copyWith(employees: employees, isLoading: false);
      } else {
        state = state.copyWith(isLoading: false, error: 'Failed to load employees');
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> fetchEmployee(int userId) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.getEmployee(userId);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final employee = EmployeeProfile.fromJson(data);
        final updatedEmployees = List<EmployeeProfile>.from(state.employees);
        final index = updatedEmployees.indexWhere((e) => e.id == employee.id);
        if (index >= 0) {
          updatedEmployees[index] = employee;
        } else {
          updatedEmployees.add(employee);
        }
        state = state.copyWith(employees: updatedEmployees, isLoading: false);
      } else {
        state = state.copyWith(isLoading: false, error: 'Failed to load employee');
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> updateEmployee(int userId, Map<String, dynamic> updateData) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.updateEmployee(userId, updateData);
      if (response.statusCode == 200) {
        await fetchEmployee(userId);
      } else {
        state = state.copyWith(isLoading: false, error: 'Failed to update employee');
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  // Additional methods for create, update, delete can be added here

  Future<void> createEmployee({
    required int userId,
    required int companyId,
    String? department,
    String? position,
    String? phone,
    DateTime? hireDate,
    int? managerId,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final employeeData = {
        'user_id': userId,
        'company_id': companyId,
        'department': department,
        'position': position,
        'phone': phone,
        'hire_date': hireDate?.toIso8601String(),
        'manager_id': managerId,
      };
      final response = await _apiService.createEmployee(employeeData);
      if (response.statusCode == 201) {
        final newEmployee = EmployeeProfile.fromJson(json.decode(response.body));
        final updatedEmployees = List<EmployeeProfile>.from(state.employees)..add(newEmployee);
        state = state.copyWith(employees: updatedEmployees, isLoading: false);
      } else {
        final errorMsg = 'Failed to create employee: ${response.statusCode}';
        state = state.copyWith(isLoading: false, error: errorMsg);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final employeesProvider = StateNotifierProvider<EmployeesNotifier, EmployeesState>((ref) {
  final apiService = ApiService();
  return EmployeesNotifier(apiService);
});
