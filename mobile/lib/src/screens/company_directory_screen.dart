import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/providers/company_directory_provider.dart';

class CompanyDirectoryScreen extends ConsumerStatefulWidget {
  final int companyId;

  const CompanyDirectoryScreen({super.key, required this.companyId});

  @override
  ConsumerState<CompanyDirectoryScreen> createState() => _CompanyDirectoryScreenState();
}

class _CompanyDirectoryScreenState extends ConsumerState<CompanyDirectoryScreen> {
  String? _selectedDepartment;
  String? _selectedPosition;
  String _sortBy = 'full_name';
  String _sortOrder = 'asc';

  @override
  void initState() {
    super.initState();
    ref.read(companyDirectoryProvider(widget.companyId).notifier).initialize();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(companyDirectoryProvider(widget.companyId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Company Directory'),
      ),
      body: Column(
        children: [
          // Filters
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                // Department Dropdown
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _selectedDepartment,
                    decoration: const InputDecoration(
                      labelText: 'Department',
                      border: OutlineInputBorder(),
                    ),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All Departments')),
                      ...state.departments.map((dept) => DropdownMenuItem(value: dept, child: Text(dept))),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedDepartment = value;
                      });
                      ref.read(companyDirectoryProvider(widget.companyId).notifier).setFilters(
                            department: value,
                            position: _selectedPosition,
                          );
                    },
                  ),
                ),
                const SizedBox(width: 8),
                // Position Dropdown
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _selectedPosition,
                    decoration: const InputDecoration(
                      labelText: 'Position',
                      border: OutlineInputBorder(),
                    ),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All Positions')),
                      ...state.positions.map((pos) => DropdownMenuItem(value: pos, child: Text(pos))),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedPosition = value;
                      });
                      ref.read(companyDirectoryProvider(widget.companyId).notifier).setFilters(
                            department: _selectedDepartment,
                            position: value,
                          );
                    },
                  ),
                ),
              ],
            ),
          ),
          // Sorting Options
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8.0),
            child: Row(
              children: [
                const Text('Sort by:'),
                const SizedBox(width: 8),
                DropdownButton<String>(
                  value: _sortBy,
                  items: const [
                    DropdownMenuItem(value: 'full_name', child: Text('Name')),
                    DropdownMenuItem(value: 'role', child: Text('Role')),
                    DropdownMenuItem(value: 'department', child: Text('Department')),
                    DropdownMenuItem(value: 'position', child: Text('Position')),
                  ],
                  onChanged: (value) {
                    if (value != null) {
                      setState(() {
                        _sortBy = value;
                      });
                      ref.read(companyDirectoryProvider(widget.companyId).notifier).setSorting(_sortBy, _sortOrder);
                    }
                  },
                ),
                const SizedBox(width: 16),
                DropdownButton<String>(
                  value: _sortOrder,
                  items: const [
                    DropdownMenuItem(value: 'asc', child: Text('Ascending')),
                    DropdownMenuItem(value: 'desc', child: Text('Descending')),
                  ],
                  onChanged: (value) {
                    if (value != null) {
                      setState(() {
                        _sortOrder = value;
                      });
                      ref.read(companyDirectoryProvider(widget.companyId).notifier).setSorting(_sortBy, _sortOrder);
                    }
                  },
                ),
              ],
            ),
          ),
          // User List
          Expanded(
            child: state.isLoading
                ? const Center(child: CircularProgressIndicator())
                : state.error != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.error, size: 48, color: Colors.red),
                            const SizedBox(height: 16),
                            Text('Error: ${state.error}'),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: () {
                                ref.read(companyDirectoryProvider(widget.companyId).notifier).fetchUsers();
                              },
                              child: const Text('Retry'),
                            ),
                          ],
                        ),
                      )
                    : state.users.isEmpty
                        ? const Center(
                            child: Text('No users found'),
                          )
                        : ListView.builder(
                            itemCount: state.users.length,
                            itemBuilder: (context, index) {
                              final user = state.users[index];
                              return ListTile(
                                title: Text(user.fullName ?? 'User'),
                                subtitle: Text('${user.role} - ${user.employeeProfile?.department ?? 'No Department'}'),
                                trailing: user.isActive
                                    ? const Icon(Icons.check_circle, color: Colors.green)
                                    : const Icon(Icons.cancel, color: Colors.red),
                                onTap: () {
                                  // TODO: Navigate to user profile details screen
                                },
                              );
                            },
                          ),
          ),
        ],
      ),
    );
  }
}
