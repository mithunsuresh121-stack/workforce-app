import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../providers/auth_provider.dart';
import 'dart:convert';

class NotificationPreferencesScreen extends ConsumerStatefulWidget {
  const NotificationPreferencesScreen({super.key});

  @override
  ConsumerState<NotificationPreferencesScreen> createState() => _NotificationPreferencesScreenState();
}

class _NotificationPreferencesScreenState extends ConsumerState<NotificationPreferencesScreen> {
  bool _isLoading = true;
  Map<String, dynamic> _preferences = {};
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    try {
      final response = await _apiService.getNotificationPreferences();
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _preferences = data['preferences'] ?? {};
          _isLoading = false;
        });
      } else {
        // If no preferences exist, load defaults
        setState(() {
          _preferences = {
            "mute_all": false,
            "digest_mode": "immediate",
            "push_enabled": true,
            "notification_types": {
              "TASK_ASSIGNED": true,
              "SHIFT_SCHEDULED": true,
              "SYSTEM_MESSAGE": true,
              "ADMIN_MESSAGE": true
            }
          };
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _preferences = {
          "mute_all": false,
          "digest_mode": "immediate",
          "push_enabled": true,
          "notification_types": {
            "TASK_ASSIGNED": true,
            "SHIFT_SCHEDULED": true,
            "SYSTEM_MESSAGE": true,
            "ADMIN_MESSAGE": true
          }
        };
        _isLoading = false;
      });
    }
  }

  Future<void> _savePreferences() async {
    try {
      final response = await _apiService.updateNotificationPreferences(_preferences);
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Preferences saved successfully')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to save preferences')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error saving preferences')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notification Preferences'),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
        foregroundColor: Theme.of(context).colorScheme.onPrimaryContainer,
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: _savePreferences,
            tooltip: 'Save Preferences',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // General Settings
            const Text(
              'General Settings',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('Mute All Notifications'),
              subtitle: const Text('Disable all notifications'),
              value: _preferences['mute_all'] ?? false,
              onChanged: (value) {
                setState(() {
                  _preferences['mute_all'] = value;
                });
              },
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('Push Notifications'),
              subtitle: const Text('Receive push notifications on mobile'),
              value: _preferences['push_enabled'] ?? true,
              onChanged: (_preferences['mute_all'] ?? false)
                  ? null
                  : (value) {
                      setState(() {
                        _preferences['push_enabled'] = value;
                      });
                    },
            ),
            const SizedBox(height: 16),
            const Text(
              'Digest Mode',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _preferences['digest_mode'] ?? 'immediate',
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              ),
              items: const [
                DropdownMenuItem(value: 'immediate', child: Text('Immediate')),
                DropdownMenuItem(value: 'daily', child: Text('Daily Digest')),
                DropdownMenuItem(value: 'weekly', child: Text('Weekly Digest')),
              ],
              onChanged: (_preferences['mute_all'] ?? false)
                  ? null
                  : (value) {
                      setState(() {
                        _preferences['digest_mode'] = value;
                      });
                    },
            ),
            const SizedBox(height: 32),

            // Notification Types
            const Text(
              'Notification Types',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildNotificationTypeTile('Task Assignments', 'TASK_ASSIGNED'),
            _buildNotificationTypeTile('Shift Schedules', 'SHIFT_SCHEDULED'),
            _buildNotificationTypeTile('System Messages', 'SYSTEM_MESSAGE'),
            _buildNotificationTypeTile('Admin Messages', 'ADMIN_MESSAGE'),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationTypeTile(String title, String typeKey) {
    final notificationTypes = _preferences['notification_types'] as Map<String, dynamic>? ?? {};
    final isEnabled = notificationTypes[typeKey] ?? true;

    return SwitchListTile(
      title: Text(title),
      value: isEnabled,
      onChanged: (_preferences['mute_all'] ?? false)
          ? null
          : (value) {
              setState(() {
                _preferences['notification_types'][typeKey] = value;
              });
            },
    );
  }
}
