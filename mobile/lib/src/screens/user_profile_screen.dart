import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/providers/user_profile_provider.dart';
import 'package:workforce_app/src/providers/auth_provider.dart';

class UserProfileScreen extends ConsumerStatefulWidget {
  const UserProfileScreen({super.key});

  @override
  ConsumerState<UserProfileScreen> createState() => _UserProfileScreenState();
}

class _UserProfileScreenState extends ConsumerState<UserProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _fullNameController;
  late TextEditingController _emailController;
  late TextEditingController _departmentController;
  late TextEditingController _positionController;
  late TextEditingController _phoneController;
  DateTime? _hireDate;
  bool _isEditing = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _fullNameController = TextEditingController();
    _emailController = TextEditingController();
    _departmentController = TextEditingController();
    _positionController = TextEditingController();
    _phoneController = TextEditingController();

    // Fetch user profile when screen loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(userProfileProvider.notifier).fetchUserProfile();
    });
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _departmentController.dispose();
    _positionController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final profileState = ref.watch(userProfileProvider);
    final authState = ref.watch(authProvider);

    // Role-based UI control: disable editing if user role is not allowed
    final allowedRoles = ['SuperAdmin', 'CompanyAdmin', 'Manager'];
    final canEdit = allowedRoles.contains(authState.role) || authState.email == profileState.profile?.email;

    // Update controllers when profile data is loaded
    if (profileState.profile != null && !_isEditing) {
      _fullNameController.text = profileState.profile!.fullName ?? '';
      _emailController.text = profileState.profile!.email;
      if (profileState.profile!.employeeProfile != null) {
        _departmentController.text = profileState.profile!.employeeProfile!.department ?? '';
        _positionController.text = profileState.profile!.employeeProfile!.position ?? '';
        _phoneController.text = profileState.profile!.employeeProfile!.phone ?? '';
        _hireDate = profileState.profile!.employeeProfile!.hireDate;
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        actions: [
          if (!_isEditing)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => setState(() => _isEditing = true),
            )
          else
            IconButton(
              icon: const Icon(Icons.cancel),
              onPressed: () => setState(() => _isEditing = false),
            ),
        ],
      ),
      body: profileState.isLoading && profileState.profile == null
          ? const Center(child: CircularProgressIndicator())
          : profileState.error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error, size: 48, color: Colors.red),
                      const SizedBox(height: 16),
                      Text('Error: ${profileState.error}'),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () {
                          ref.read(userProfileProvider.notifier).fetchUserProfile();
                        },
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : profileState.profile == null
                  ? const Center(
                      child: Text('No profile data available'),
                    )
                  : SingleChildScrollView(
                      padding: const EdgeInsets.all(16),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Profile Header
                            Center(
                              child: Column(
                                children: [
                                  CircleAvatar(
                                    radius: 50,
                                    backgroundColor: Theme.of(context).colorScheme.primary,
                                    child: Text(
                                      profileState.profile!.fullName?.substring(0, 1).toUpperCase() ?? 'U',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 32,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    profileState.profile!.fullName ?? 'User',
                                    style: Theme.of(context).textTheme.headlineSmall,
                                  ),
                                  Text(
                                    profileState.profile!.role,
                                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                      color: Colors.grey,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 32),

                            // Basic Information
                            const Text(
                              'Basic Information',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 16),

                            TextFormField(
                              controller: _emailController,
                              decoration: const InputDecoration(
                                labelText: 'Email',
                                border: OutlineInputBorder(),
                              ),
                              enabled: false, // Email should not be editable
                            ),
                            const SizedBox(height: 16),

                            TextFormField(
                              controller: _fullNameController,
                              decoration: const InputDecoration(
                                labelText: 'Full Name',
                                border: OutlineInputBorder(),
                              ),
                              enabled: _isEditing,
                              validator: (value) {
                                if (value?.isEmpty ?? true) {
                                  return 'Full name is required';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 32),

                            // Employee Information
                            if (profileState.profile!.employeeProfile != null) ...[
                              const Text(
                                'Employee Information',
                                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 16),

                              TextFormField(
                                controller: _departmentController,
                                decoration: const InputDecoration(
                                  labelText: 'Department',
                                  border: OutlineInputBorder(),
                                ),
                                enabled: _isEditing,
                              ),
                              const SizedBox(height: 16),

                              TextFormField(
                                controller: _positionController,
                                decoration: const InputDecoration(
                                  labelText: 'Position',
                                  border: OutlineInputBorder(),
                                ),
                                enabled: _isEditing,
                              ),
                              const SizedBox(height: 16),

                              TextFormField(
                                controller: _phoneController,
                              decoration: const InputDecoration(
                                labelText: 'Phone',
                                border: OutlineInputBorder(),
                              ),
                              enabled: canEdit && _isEditing,
                              keyboardType: TextInputType.phone,
                              validator: (value) {
                                if (value != null && value.isNotEmpty) {
                                  final phoneRegex = RegExp(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$');
                                  if (!phoneRegex.hasMatch(value)) {
                                    return 'Please enter a valid phone number';
                                  }
                                }
                                return null;
                              },
                            ),
                              const SizedBox(height: 16),

                              InkWell(
                                onTap: (canEdit && _isEditing) ? () async {
                                  final date = await showDatePicker(
                                    context: context,
                                    initialDate: _hireDate ?? DateTime.now(),
                                    firstDate: DateTime(2000),
                                    lastDate: DateTime.now(),
                                  );
                                  if (date != null) {
                                    setState(() => _hireDate = date);
                                  }
                                } : null,
                                child: InputDecorator(
                                  decoration: const InputDecoration(
                                    labelText: 'Hire Date',
                                    border: OutlineInputBorder(),
                                    suffixIcon: Icon(Icons.calendar_today),
                                  ),
                                  child: Text(
                                    _hireDate != null
                                        ? '${_hireDate!.month}/${_hireDate!.day}/${_hireDate!.year}'
                                        : 'Not set',
                                  ),
                                ),
                              ),
                            ],

                            const SizedBox(height: 32),

                            // Action Buttons
                            if (canEdit && _isEditing) ...[
                              Row(
                                children: [
                                  Expanded(
                                    child: OutlinedButton(
                                      onPressed: () => setState(() => _isEditing = false),
                                      child: const Text('Cancel'),
                                    ),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: ElevatedButton(
                                      onPressed: _isLoading ? null : _saveProfile,
                                      child: _isLoading
                                          ? const SizedBox(
                                              width: 20,
                                              height: 20,
                                              child: CircularProgressIndicator(strokeWidth: 2),
                                            )
                                          : const Text('Save Changes'),
                                    ),
                                  ),
                                ],
                              ),
                            ],

                            // Error Display
                            if (profileState.error != null && !_isEditing)
                              Container(
                                padding: const EdgeInsets.all(8.0),
                                margin: const EdgeInsets.only(top: 16),
                                color: Colors.red[100],
                                child: Row(
                                  children: [
                                    const Icon(Icons.error_outline, color: Colors.red),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        profileState.error!,
                                        style: const TextStyle(color: Colors.red),
                                      ),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.close),
                                      onPressed: () {
                                        ref.read(userProfileProvider.notifier).clearError();
                                      },
                                    ),
                                  ],
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
    );
  }

  void _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final updateData = {
        'user': {
          'full_name': _fullNameController.text,
        },
        'employee_profile': {
          'department': _departmentController.text.isNotEmpty ? _departmentController.text : null,
          'position': _positionController.text.isNotEmpty ? _positionController.text : null,
          'phone': _phoneController.text.isNotEmpty ? _phoneController.text : null,
          'hire_date': _hireDate?.toIso8601String(),
        },
      };

      await ref.read(userProfileProvider.notifier).updateUserProfile(updateData);

      final profileState = ref.read(userProfileProvider);
      if (profileState.error != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${profileState.error}')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated successfully')),
        );
        setState(() => _isEditing = false);
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }
}
