import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';

class Shift {
  final int id;
  final int employeeId;
  final String shiftName;
  final DateTime shiftDate;
  final String shiftTime;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;

  Shift({
    required this.id,
    required this.employeeId,
    required this.shiftName,
    required this.shiftDate,
    required this.shiftTime,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Shift.fromJson(Map<String, dynamic> json) {
    return Shift(
      id: json['id'],
      employeeId: json['employee_id'],
      shiftName: json['shift_name'],
      shiftDate: DateTime.parse(json['shift_date']),
      shiftTime: json['shift_time'],
      status: json['status'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'employee_id': employeeId,
      'shift_name': shiftName,
      'shift_date': shiftDate.toIso8601String(),
      'shift_time': shiftTime,
      'status': status,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class ShiftsState {
  final List<Shift> shifts;
  final bool isLoading;
  final String? error;

  ShiftsState({
    this.shifts = const [],
    this.isLoading = false,
    this.error,
  });

  ShiftsState copyWith({
    List<Shift>? shifts,
    bool? isLoading,
    String? error,
  }) {
    return ShiftsState(
      shifts: shifts ?? this.shifts,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class ShiftsNotifier extends StateNotifier<ShiftsState> {
  final ApiService _apiService;

  ShiftsNotifier(this._apiService) : super(ShiftsState());

  Future<void> fetchShifts() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.getShifts();
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        final shifts = data.map((e) => Shift.fromJson(e)).toList();
        state = state.copyWith(shifts: shifts, isLoading: false);
      } else {
        state = state.copyWith(isLoading: false, error: 'Failed to load shifts');
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> createShift({
    required int employeeId,
    required String shiftName,
    required DateTime shiftDate,
    required String shiftTime,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final shiftData = {
        'employee_id': employeeId,
        'shift_name': shiftName,
        'shift_date': shiftDate.toIso8601String(),
        'shift_time': shiftTime,
      };
      final response = await _apiService.createShift(shiftData);
      if (response.statusCode == 201) {
        final newShift = Shift.fromJson(json.decode(response.body));
        final updatedShifts = List<Shift>.from(state.shifts)..add(newShift);
        state = state.copyWith(shifts: updatedShifts, isLoading: false);
      } else {
        final errorMsg = 'Failed to create shift: ${response.statusCode}';
        state = state.copyWith(isLoading: false, error: errorMsg);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> updateShiftStatus(int shiftId, String status) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _apiService.updateShiftStatus(shiftId, status);
      if (response.statusCode == 200) {
        final updatedShift = Shift.fromJson(json.decode(response.body));
        final updatedShifts = state.shifts.map((shift) {
          return shift.id == shiftId ? updatedShift : shift;
        }).toList();
        state = state.copyWith(shifts: updatedShifts, isLoading: false);
      } else {
        final errorMsg = 'Failed to update shift status: ${response.statusCode}';
        state = state.copyWith(isLoading: false, error: errorMsg);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final shiftsProvider = StateNotifierProvider<ShiftsNotifier, ShiftsState>((ref) {
  final apiService = ApiService();
  return ShiftsNotifier(apiService);
});
