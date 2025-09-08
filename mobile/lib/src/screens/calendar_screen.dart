import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  _CalendarScreenState createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  final ApiService _apiService = ApiService();
  CalendarFormat _calendarFormat = CalendarFormat.month;
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;
  Map<DateTime, List<Map<String, dynamic>>> _events = {};
  List<Map<String, dynamic>> _shifts = [];
  List<Map<String, dynamic>> _tasks = [];
  bool _isLoading = true;
  bool _isRetrying = false;
  int _retryCount = 0;
  static const int _maxRetries = 3;

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
        _loadTasks(),
      ]);
      _buildEventsMap();
      _retryCount = 0; // Reset retry count on success
    } catch (e) {
      if (_retryCount < _maxRetries) {
        _retryCount++;
        setState(() => _isRetrying = true);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading calendar data. Retrying... ($_retryCount/$_maxRetries)'),
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
            content: Text('Failed to load calendar data after $_maxRetries attempts: $e'),
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

  Future<void> _loadTasks() async {
    try {
      final response = await _apiService.getTasks();
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        setState(() {
          _tasks = data.map((item) => item as Map<String, dynamic>).toList();
        });
      }
    } catch (e) {
      print('Error loading tasks: $e');
    }
  }

  void _buildEventsMap() {
    _events.clear();

    // Add shifts to events
    for (var shift in _shifts) {
      final startDate = DateTime.parse(shift['start_at']).toLocal();
      final endDate = DateTime.parse(shift['end_at']).toLocal();
      final eventDate = DateTime(startDate.year, startDate.month, startDate.day);

      if (!_events.containsKey(eventDate)) {
        _events[eventDate] = [];
      }

      _events[eventDate]!.add({
        'type': 'shift',
        'title': 'Shift: ${DateFormat('HH:mm').format(startDate)} - ${DateFormat('HH:mm').format(endDate)}',
        'data': shift,
        'color': Colors.blue,
      });
    }

    // Add tasks to events
    for (var task in _tasks) {
      if (task['due_at'] != null) {
        final dueDate = DateTime.parse(task['due_at']).toLocal();
        final eventDate = DateTime(dueDate.year, dueDate.month, dueDate.day);

        if (!_events.containsKey(eventDate)) {
          _events[eventDate] = [];
        }

        _events[eventDate]!.add({
          'type': 'task',
          'title': 'Task: ${task['title']}',
          'data': task,
          'color': _getTaskColor(task['status']),
        });
      }
    }
  }

  Color _getTaskColor(String status) {
    final theme = Theme.of(context);
    switch (status) {
      case 'Pending':
        return theme.colorScheme.secondary;
      case 'In Progress':
        return theme.colorScheme.primary;
      case 'Completed':
        return theme.colorScheme.tertiary;
      case 'Overdue':
        return theme.colorScheme.error;
      default:
        return theme.colorScheme.onSurface.withOpacity(0.5);
    }
  }

  List<Map<String, dynamic>> _getEventsForDay(DateTime day) {
    final eventDate = DateTime(day.year, day.month, day.day);
    return _events[eventDate] ?? [];
  }

  void _onDaySelected(DateTime selectedDay, DateTime focusedDay) {
    setState(() {
      _selectedDay = selectedDay;
      _focusedDay = focusedDay;
    });
  }

  void _showEventDetails(Map<String, dynamic> event) {
    final theme = Theme.of(context);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Semantics(
          label: 'Event details dialog',
          child: Text(event['title']),
        ),
        content: Semantics(
          label: 'Event information',
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Semantics(
                label: 'Event type',
                child: Text(
                  'Type: ${event['type'].toUpperCase()}',
                  style: theme.textTheme.bodyMedium,
                ),
              ),
              if (event['type'] == 'shift') ...[
                Semantics(
                  label: 'Shift location',
                  child: Text(
                    'Location: ${event['data']['location'] ?? 'N/A'}',
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
                Semantics(
                  label: 'Shift start time',
                  child: Text(
                    'Start: ${DateFormat('MMM dd, yyyy HH:mm').format(DateTime.parse(event['data']['start_at']))}',
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
                Semantics(
                  label: 'Shift end time',
                  child: Text(
                    'End: ${DateFormat('MMM dd, yyyy HH:mm').format(DateTime.parse(event['data']['end_at']))}',
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
              ] else ...[
                Semantics(
                  label: 'Task status',
                  child: Text(
                    'Status: ${event['data']['status']}',
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
                Semantics(
                  label: 'Task priority',
                  child: Text(
                    'Priority: ${event['data']['priority'] ?? 'N/A'}',
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
                if (event['data']['description'] != null)
                  Semantics(
                    label: 'Task description',
                    child: Text(
                      'Description: ${event['data']['description']}',
                      style: theme.textTheme.bodyMedium,
                    ),
                  ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Semantics(
          label: 'Calendar Screen',
          hint: 'View and manage your schedule',
          child: const Text('Calendar'),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: 'Refresh calendar data',
          ),
        ],
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isSmallScreen = constraints.maxWidth < 600;
          return _isLoading
              ? Center(
                  child: Semantics(
                    label: 'Loading calendar data',
                    child: const CircularProgressIndicator(),
                  ),
                )
              : Column(
                  children: [
                    Semantics(
                      label: 'Calendar widget',
                      hint: 'Navigate through dates and view events',
                      child: TableCalendar(
                        firstDay: DateTime.utc(2020, 1, 1),
                        lastDay: DateTime.utc(2030, 12, 31),
                        focusedDay: _focusedDay,
                        calendarFormat: _calendarFormat,
                        selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
                        eventLoader: _getEventsForDay,
                        onDaySelected: _onDaySelected,
                        onFormatChanged: (format) {
                          setState(() => _calendarFormat = format);
                        },
                        onPageChanged: (focusedDay) {
                          _focusedDay = focusedDay;
                        },
                        calendarStyle: CalendarStyle(
                          markersMaxCount: 3,
                          markerDecoration: BoxDecoration(
                            color: theme.colorScheme.primary,
                            shape: BoxShape.circle,
                          ),
                          selectedDecoration: BoxDecoration(
                            color: theme.colorScheme.primaryContainer,
                            shape: BoxShape.circle,
                          ),
                          todayDecoration: BoxDecoration(
                            color: theme.colorScheme.secondaryContainer,
                            shape: BoxShape.circle,
                          ),
                        ),
                        headerStyle: HeaderStyle(
                          formatButtonDecoration: BoxDecoration(
                            color: theme.colorScheme.primaryContainer,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          formatButtonTextStyle: TextStyle(
                            color: theme.colorScheme.onPrimaryContainer,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8.0),
                    Expanded(
                      child: _selectedDay != null
                          ? Semantics(
                              label: 'Events for selected day',
                              child: _buildEventList(_getEventsForDay(_selectedDay!)),
                            )
                          : Center(
                              child: Semantics(
                                label: 'No day selected',
                                hint: 'Tap on a date to view events',
                                child: Text(
                                  'Select a day to view events',
                                  style: theme.textTheme.bodyLarge,
                                ),
                              ),
                            ),
                    ),
                  ],
                );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddEventDialog(),
        tooltip: 'Add new event',
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildEventList(List<Map<String, dynamic>> events) {
    final theme = Theme.of(context);
    if (events.isEmpty) {
      return Center(
        child: Semantics(
          label: 'No events found',
          hint: 'There are no scheduled events for the selected day',
          child: Text(
            'No events for this day',
            style: theme.textTheme.bodyLarge,
          ),
        ),
      );
    }

    return Semantics(
      label: 'List of events',
      hint: 'Tap on an event to view details',
      child: ListView.builder(
        itemCount: events.length,
        itemBuilder: (context, index) {
          final event = events[index];
          return Focus(
            autofocus: index == 0,
            child: Card(
              margin: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
              color: theme.cardColor,
              child: ListTile(
                leading: Semantics(
                  label: '${event['type']} indicator',
                  child: CircleAvatar(
                    backgroundColor: event['color'],
                    radius: 8,
                  ),
                ),
                title: Semantics(
                  label: 'Event title: ${event['title']}',
                  child: Text(
                    event['title'],
                    style: theme.textTheme.titleMedium,
                  ),
                ),
                subtitle: Semantics(
                  label: 'Event type: ${event['type']}',
                  child: Text(
                    event['type'].toUpperCase(),
                    style: theme.textTheme.bodySmall,
                  ),
                ),
                onTap: () => _showEventDetails(event),
              ),
            ),
          );
        },
      ),
    );
  }

  void _showAddEventDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Event'),
        content: const Text('Event creation will be implemented in the next phase.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}
