import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class ShiftManagementScreen extends StatefulWidget {
  @override
  _ShiftManagementScreenState createState() => _ShiftManagementScreenState();
}

class _ShiftManagementScreenState extends State<ShiftManagementScreen> {
  final ApiService _apiService = ApiService();
  final _formKey = GlobalKey<FormState>();
  List<Map<String, dynamic>> _shifts = [];
  List<Map<String, dynamic>> _employees = [];
  bool _isLoading = true;
  bool _isSubmitting = false;
  bool _isRetrying = false;
  int _retryCount = 0;
  static const int _maxRetries = 3;

  final TextEditingController _startDateController = TextEditingController();
  final TextEditingController _startTimeController = TextEditingController();
  final TextEditingController _endDateController = TextEditingController();
  final TextEditingController _endTimeController = TextEditingController();
  final TextEditingController _locationController = TextEditingController();

  int? _selectedEmployeeId;
  DateTime? _startDateTime;
  DateTime? _endDateTime;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      await Future.wait([
        _loadShifts(),
        _loadEmployees(),
      ]);
      _retryCount = 0; // Reset retry count on success
    } catch (e) {
      if (_retryCount < _maxRetries) {
        _retryCount++;
        setState(() => _isRetrying = true);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading data. Retrying... ($_retryCount/$_maxRetries)'),
            action: SnackBarAction(
              label: 'Retry Now',
              onPressed: () => _loadData(),
            ),
          ),
        );
        await Future.delayed(const Duration(seconds: 2));
        setState(() => _isRetrying = false);
        await _loadData();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load data after $_maxRetries attempts: $e'),
            action: SnackBarAction(
              label: 'Retry',
              onPressed: () => _loadData(),
            ),
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
        _isRetrying = false;
      });
    }
  }

  Future<void> _loadShifts() async {
    try {
      final response = await _apiService.getShifts();
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        setState(() {
          _shifts = data.map((item) => item as Map<String, dynamic>).toList();
        });
      }
    } catch (e) {
      print('Error loading shifts: $e');
    }
  }

  Future<void> _loadEmployees() async {
    try {
      final response = await _apiService.getEmployees();
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        setState(() {
          _employees = data.map((item) => item as Map<String, dynamic>).toList();
        });
      }
    } catch (e) {
      print('Error loading employees: $e');
    }
  }

  Future<void> _submitShift() async {
    if (!_formKey.currentState!.validate()) return;

    if (_selectedEmployeeId == null || _startDateTime == null || _endDateTime == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all required fields')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      // Get current user profile to get company_id
      final userResponse = await _apiService.getCurrentUserProfile();
      if (userResponse.statusCode != 200) {
        throw Exception('Failed to get user profile');
      }

      final userData = json.decode(userResponse.body);
      final companyId = userData['company_id']?.toString() ?? 'default';

      final shiftData = {
        'tenant_id': companyId,
        'employee_id': _selectedEmployeeId,
        'start_at': _startDateTime!.toUtc().toIso8601String(),
        'end_at': _endDateTime!.toUtc().toIso8601String(),
        'location': _locationController.text.trim().isEmpty ? null : _locationController.text.trim(),
      };

      final response = await _apiService.createShift(shiftData);

      if (response.statusCode == 201) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Shift created successfully')),
        );
        _clearForm();
        await _loadShifts();
      } else {
        final error = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${error['detail'] ?? 'Failed to create shift'}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error creating shift: $e')),
      );
    } finally {
      setState(() => _isSubmitting = false);
    }
  }

  void _clearForm() {
    _startDateController.clear();
    _startTimeController.clear();
    _endDateController.clear();
    _endTimeController.clear();
    _locationController.clear();
    setState(() {
      _selectedEmployeeId = null;
      _startDateTime = null;
      _endDateTime = null;
    });
  }

  Future<void> _selectDateTime(bool isStart) async {
    final date = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );

    if (date != null) {
      final time = await showTimePicker(
        context: context,
        initialTime: TimeOfDay.now(),
      );

      if (time != null) {
        final dateTime = DateTime(date.year, date.month, date.day, time.hour, time.minute);
        setState(() {
          if (isStart) {
            _startDateTime = dateTime;
            _startDateController.text = DateFormat('yyyy-MM-dd').format(dateTime);
            _startTimeController.text = DateFormat('HH:mm').format(dateTime);
          } else {
            _endDateTime = dateTime;
            _endDateController.text = DateFormat('yyyy-MM-dd').format(dateTime);
            _endTimeController.text = DateFormat('HH:mm').format(dateTime);
          }
        });
      }
    }
  }

  Future<void> _deleteShift(int shiftId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Shift'),
        content: const Text('Are you sure you want to delete this shift?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        final response = await _apiService.deleteShift(shiftId);
        if (response.statusCode == 200) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Shift deleted successfully')),
          );
          await _loadShifts();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to delete shift')),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting shift: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _startDateController.dispose();
    _startTimeController.dispose();
    _endDateController.dispose();
    _endTimeController.dispose();
    _locationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Semantics(
          label: 'Shift Management Screen',
          hint: 'Create and manage employee shifts',
          child: const Text('Shift Management'),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: 'Refresh shift data',
          ),
        ],
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isSmallScreen = constraints.maxWidth < 600;
          return _isLoading
              ? Center(
                  child: Semantics(
                    label: 'Loading shift data',
                    child: const CircularProgressIndicator(),
                  ),
                )
              : Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Expanded(
                        flex: 2,
                        child: Card(
                          color: theme.cardColor,
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Form(
                              key: _formKey,
                              child: ListView(
                                children: [
                                  Semantics(
                                    label: 'Create New Shift Form',
                                    child: Text(
                                      'Create New Shift',
                                      style: theme.textTheme.headlineSmall,
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  DropdownButtonFormField<int>(
                                    value: _selectedEmployeeId,
                                    decoration: InputDecoration(
                                      labelText: 'Employee',
                                      border: const OutlineInputBorder(),
                                      filled: true,
                                      fillColor: theme.inputDecorationTheme.fillColor,
                                    ),
                                    items: _employees.map((employee) {
                                      return DropdownMenuItem<int>(
                                        value: employee['id'],
                                        child: Text(employee['full_name'] ?? 'Employee ${employee['id']}'),
                                      );
                                    }).toList(),
                                    onChanged: (value) {
                                      setState(() => _selectedEmployeeId = value);
                                    },
                                    validator: (value) {
                                      if (value == null) {
                                        return 'Please select an employee';
                                      }
                                      return null;
                                    },
                                  ),
                                  const SizedBox(height: 16),
                                  Row(
                                    children: [
                                      Expanded(
                                        child: TextFormField(
                                          controller: _startDateController,
                                          decoration: InputDecoration(
                                            labelText: 'Start Date',
                                            border: const OutlineInputBorder(),
                                            filled: true,
                                            fillColor: theme.inputDecorationTheme.fillColor,
                                          ),
                                          readOnly: true,
                                          onTap: () => _selectDateTime(true),
                                          validator: (value) {
                                            if (value == null || value.isEmpty) {
                                              return 'Please select start date';
                                            }
                                            return null;
                                          },
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: TextFormField(
                                          controller: _startTimeController,
                                          decoration: InputDecoration(
                                            labelText: 'Start Time',
                                            border: const OutlineInputBorder(),
                                            filled: true,
                                            fillColor: theme.inputDecorationTheme.fillColor,
                                          ),
                                          readOnly: true,
                                          onTap: () => _selectDateTime(true),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 16),
                                  Row(
                                    children: [
                                      Expanded(
                                        child: TextFormField(
                                          controller: _endDateController,
                                          decoration: InputDecoration(
                                            labelText: 'End Date',
                                            border: const OutlineInputBorder(),
                                            filled: true,
                                            fillColor: theme.inputDecorationTheme.fillColor,
                                          ),
                                          readOnly: true,
                                          onTap: () => _selectDateTime(false),
                                          validator: (value) {
                                            if (value == null || value.isEmpty) {
                                              return 'Please select end date';
                                            }
                                            return null;
                                          },
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: TextFormField(
                                          controller: _endTimeController,
                                          decoration: InputDecoration(
                                            labelText: 'End Time',
                                            border: const OutlineInputBorder(),
                                            filled: true,
                                            fillColor: theme.inputDecorationTheme.fillColor,
                                          ),
                                          readOnly: true,
                                          onTap: () => _selectDateTime(false),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 16),
                                  TextFormField(
                                    controller: _locationController,
                                    decoration: InputDecoration(
                                      labelText: 'Location (Optional)',
                                      border: const OutlineInputBorder(),
                                      filled: true,
                                      fillColor: theme.inputDecorationTheme.fillColor,
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  ElevatedButton(
                                    onPressed: _isSubmitting ? null : _submitShift,
                                    child: _isSubmitting
                                        ? const CircularProgressIndicator()
                                        : const Text('Create Shift'),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Expanded(
                        flex: 3,
                        child: Card(
                          color: theme.cardColor,
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Semantics(
                                  label: 'Scheduled Shifts List',
                                  child: Text(
                                    'Scheduled Shifts',
                                    style: theme.textTheme.headlineSmall,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Expanded(
                                  child: _shifts.isEmpty
                                      ? Center(
                                          child: Semantics(
                                            label: 'No shifts scheduled',
                                            hint: 'There are no scheduled shifts',
                                            child: Text(
                                              'No shifts scheduled',
                                              style: theme.textTheme.bodyLarge,
                                            ),
                                          ),
                                        )
                                      : ListView.builder(
                                          itemCount: _shifts.length,
                                          itemBuilder: (context, index) {
                                            final shift = _shifts[index];
                                            final startTime = DateTime.parse(shift['start_at']).toLocal();
                                            final endTime = DateTime.parse(shift['end_at']).toLocal();
                                            final employee = _employees.firstWhere(
                                              (emp) => emp['id'] == shift['employee_id'],
                                              orElse: () => {'full_name': 'Unknown Employee'},
                                            );

                                            return Focus(
                                              autofocus: index == 0,
                                              child: Card(
                                                margin: const EdgeInsets.symmetric(vertical: 4),
                                                color: theme.cardColor,
                                                child: ListTile(
                                                  title: Semantics(
                                                    label: 'Employee name',
                                                    child: Text(
                                                      '${employee['full_name'] ?? 'Employee ${shift['employee_id']}}',
                                                      style: theme.textTheme.titleMedium,
                                                    ),
                                                  ),
                                                  subtitle: Column(
                                                    crossAxisAlignment: CrossAxisAlignment.start,
                                                    children: [
                                                      Semantics(
                                                        label: 'Shift time',
                                                        child: Text(
                                                          '${DateFormat('MMM dd, yyyy HH:mm').format(startTime)} - ${DateFormat('HH:mm').format(endTime)}',
                                                          style: theme.textTheme.bodyMedium,
                                                        ),
                                                      ),
                                                      if (shift['location'] != null)
                                                        Semantics(
                                                          label: 'Shift location',
                                                          child: Text(
                                                            'Location: ${shift['location']}',
                                                            style: theme.textTheme.bodyMedium,
                                                          ),
                                                        ),
                                                    ],
                                                  ),
                                                  trailing: IconButton(
                                                    icon: const Icon(Icons.delete, color: Colors.red),
                                                    tooltip: 'Delete shift',
                                                    onPressed: () => _deleteShift(shift['id']),
                                                  ),
                                                ),
                                              ),
                                            );
                                          },
                                        ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                );
        },
      ),
    );
  }
}

