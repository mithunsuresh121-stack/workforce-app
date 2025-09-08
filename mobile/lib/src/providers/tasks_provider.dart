import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';

class Task {
  final int id;
  final String title;
  final String description;
  final String status;
  final String? priority; // Make priority optional since backend doesn't have it
  final DateTime? dueDate;
  final String? assignee;
  final int companyId;
  final DateTime createdAt;
  final DateTime updatedAt;

  Task({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    this.priority, // Make priority optional
    this.dueDate,
    this.assignee,
    required this.companyId,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      status: json['status'],
      priority: json['priority'] ?? 'Medium', // Default to Medium if not provided
      dueDate: json['due_at'] != null ? DateTime.parse(json['due_at']) : null,
      assignee: json['assignee_id']?.toString(), // Convert to string if needed
      companyId: json['company_id'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}

class TasksState {
  final List<Task> tasks;
  final bool isLoading;
  final String? error;

  TasksState({
    this.tasks = const [],
    this.isLoading = false,
    this.error,
  });

  TasksState copyWith({
    List<Task>? tasks,
    bool? isLoading,
    String? error,
  }) {
    return TasksState(
      tasks: tasks ?? this.tasks,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class TasksNotifier extends StateNotifier<TasksState> {
  final ApiService _apiService;

  TasksNotifier(this._apiService) : super(TasksState());

  Future<void> fetchTasks() async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _apiService.getTasks();
      
      if (response.statusCode == 200) {
          final List<dynamic> data = json.decode(response.body);
          final tasks = data.map((taskJson) => Task.fromJson(taskJson)).toList();
          
          state = state.copyWith(
            tasks: tasks,
            isLoading: false,
            error: null,
          );
      } else {
          state = state.copyWith(
            isLoading: false,
            error: 'Failed to fetch tasks: ${response.statusCode}',
          );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Network error: ${e.toString()}',
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

final tasksProvider = StateNotifierProvider<TasksNotifier, TasksState>((ref) {
  final apiService = ApiService();
  return TasksNotifier(apiService);
});
