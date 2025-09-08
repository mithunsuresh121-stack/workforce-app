import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';

class Leave {
  final int id;
  final int employeeId;
  final String leaveType;
  final DateTime startDate;
  final DateTime endDate;
  final String status;
  final String? reason;
  final DateTime createdAt;
  final DateTime updatedAt;

  Leave({
    required this.id,
    required this.employeeId,
    required this.leaveType,
    required this.startDate,
    required this.endDate,
    required this.status,
    this.reason,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Leave.fromJson(Map<String, dynamic> json) {
    return Leave(
      id: json['id'],
      employeeId: json['employee_id'],
      leaveType: json['leave_type'],
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      status: json['status'],
      reason: json['reason'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'employee_id': employeeId,
      'leave_type': leaveType,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
      'status': status,
      'reason': reason,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class LeavesState {
  final List<Leave> leaves;
  final bool isLoading;
  final String? error;

  LeavesState({
    this.leaves = const [],
    this.isLoading = false,
    this.error,
  });

  LeavesState copyWith({
    List<Leave>? leaves,
    bool? isLoading,
    String? error,
  }) {
    return LeavesState(
      leaves: leaves ?? this.leaves,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class LeavesNotifier extends StateNotifier<LeavesState> {
  final ApiService _apiService;

  LeavesNotifier(this._apiService) : super(LeavesState());

  Future<void> fetchLeaves() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.getLeaves();
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        final leaves = data.map((e) => Leave.fromJson(e)).toList();
        state = state.copyWith(leaves: leaves, isLoading: false);
      } else {
        state = state.copyWith(isLoading: false, error: 'Failed to load leaves');
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> createLeave({
    required int employeeId,
    required String leaveType,
    required DateTime startDate,
    required DateTime endDate,
    String? reason,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final leaveData = {
        'employee_id': employeeId,
        'leave_type': leaveType,
        'start_date': startDate.toIso8601String(),
        'end_date': endDate.toIso8601String(),
        'reason': reason,
      };
      final response = await _apiService.createLeave(leaveData);
      if (response.statusCode == 201) {
        final newLeave = Leave.fromJson(json.decode(response.body));
        final updatedLeaves = List<Leave>.from(state.leaves)..add(newLeave);
        state = state.copyWith(leaves: updatedLeaves, isLoading: false);
      } else {
        final errorMsg = 'Failed to create leave: ${response.statusCode}';
        state = state.copyWith(isLoading: false, error: errorMsg);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> updateLeaveStatus(int leaveId, String status) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.updateLeaveStatus(leaveId, status);
      if (response.statusCode == 200) {
        final updatedLeave = Leave.fromJson(json.decode(response.body));
        final updatedLeaves = state.leaves.map((leave) {
          return leave.id == leaveId ? updatedLeave : leave;
        }).toList();
        state = state.copyWith(leaves: updatedLeaves, isLoading: false);
      } else {
        final errorMsg = 'Failed to update leave status: ${response.statusCode}';
        state = state.copyWith(isLoading: false, error: errorMsg);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final leavesProvider = StateNotifierProvider<LeavesNotifier, LeavesState>((ref) {
  final apiService = ApiService();
  return LeavesNotifier(apiService);
});
