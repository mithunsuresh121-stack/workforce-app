import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';

class TasksScreen extends ConsumerStatefulWidget {
  const TasksScreen({super.key});
  @override
  ConsumerState<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends ConsumerState<TasksScreen> {
  final ApiService _apiService = ApiService();
  List<dynamic> _tasks = [];
  bool _isLoading = true;
  Map<String, dynamic>? _currentUser;

  @override
  void initState() {
    super.initState();
    _fetchCurrentUser();
    _fetchTasks();
  }

  Future<void> _fetchCurrentUser() async {
    final response = await _apiService.getCurrentUserProfile();
    if (response.statusCode == 200) {
      setState(() {
        _currentUser = json.decode(response.body);
      });
    }
  }

  Future<void> _fetchTasks() async {
    setState(() => _isLoading = true);
    final response = await _apiService.getTasks();
    if (response.statusCode == 200) {
      setState(() {
        _tasks = json.decode(response.body) as List<dynamic>;
        _isLoading = false;
      });
    } else {
      // Handle error
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tasks'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _showAddTaskDialog,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _tasks.isEmpty
              ? const Center(child: Text('No tasks available.'))
              : ListView.builder(
                  itemCount: _tasks.length,
                  itemBuilder: (context, index) {
                    final task = _tasks[index];
                    return _TaskCard(task: task);
                  },
                ),
    );
  }

  void _showAddTaskDialog() {
    showDialog(
      context: context,
      builder: (context) {
        final titleController = TextEditingController();
        final descriptionController = TextEditingController();
        return AlertDialog(
          title: const Text('Add Task'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleController,
                decoration: const InputDecoration(labelText: 'Task Title'),
              ),
              TextField(
                controller: descriptionController,
                decoration: const InputDecoration(labelText: 'Description'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                _addTask(titleController.text, descriptionController.text);
                Navigator.of(context).pop();
              },
              child: const Text('Add'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _addTask(String title, String description) async {
    if (_currentUser == null) {
      // Show error or handle unauthenticated state
      return;
    }
    final response = await _apiService.createTask({
      'title': title,
      'description': description,
      'company_id': _currentUser!['company_id'],
    });
    if (response.statusCode == 201) {
      _fetchTasks(); // Refresh the task list
    }
  }
}

class _TaskCard extends StatelessWidget {
  final dynamic task; // Replace with your task model

  const _TaskCard({required this.task});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: ListTile(
        title: Text(task['title']), // Adjust based on your task model
        subtitle: Text(task['description']), // Adjust based on your task model
        trailing: IconButton(
          icon: const Icon(Icons.delete),
          onPressed: () {
            // Implement delete task functionality
          },
        ),
      ),
    );
  }
}
