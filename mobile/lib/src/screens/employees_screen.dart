import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/providers/auth_provider.dart';
import 'package:workforce_app/src/providers/employees_provider.dart';

class EmployeesScreen extends ConsumerStatefulWidget {
  const EmployeesScreen({super.key});
  @override
  ConsumerState<EmployeesScreen> createState() => _EmployeesScreenState();
}

class _EmployeesScreenState extends ConsumerState<EmployeesScreen> {
  int _selectedTab = 0;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Fetch employees when screen loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(employeesProvider.notifier).fetchEmployees();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final employeesState = ref.watch(employeesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Employee Directory'),
        bottom: TabBar(
          onTap: (index) => setState(() => _selectedTab = index),
          tabs: const [
            Tab(text: 'Directory'),
            Tab(text: 'Attendance'),
            Tab(text: 'Leave Requests'),
            Tab(text: 'Payroll'),
          ],
        ),
      ),
      body: IndexedStack(
        index: _selectedTab,
        children: [
          _EmployeesTab(
            searchController: _searchController,
            employeesState: employeesState,
            userRole: authState.role,
          ),
          const _AttendanceTab(),
          const _LeaveRequestsTab(),
          const _PayrollTab(),
        ],
      ),
      floatingActionButton: _selectedTab == 0 && _canAddEmployee(authState.role)
          ? FloatingActionButton(
              onPressed: () => _showAddEmployeeDialog(context),
              child: const Icon(Icons.person_add),
            )
          : null,
    );
  }

  bool _canAddEmployee(String? role) {
    return role == 'SuperAdmin' || role == 'CompanyAdmin' || role == 'Manager';
  }

  void _showAddEmployeeDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => const AddEmployeeDialog(),
    );
  }
}

class _EmployeesTab extends StatelessWidget {
  final TextEditingController searchController;
  final EmployeesState employeesState;
  final String? userRole;

  const _EmployeesTab({
    required this.searchController,
    required this.employeesState,
    required this.userRole,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Employee Directory',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          TextField(
            controller: searchController,
            decoration: InputDecoration(
              hintText: 'Search employees...',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            onChanged: (value) {
              // TODO: Implement search filtering
            },
          ),
          const SizedBox(height: 16),
          Expanded(
            child: employeesState.isLoading
                ? const Center(child: CircularProgressIndicator())
                : employeesState.error != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.error, size: 48, color: Colors.red),
                            const SizedBox(height: 16),
                            Text('Error: ${employeesState.error}'),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: () {
                                // TODO: Refresh employees
                              },
                              child: const Text('Retry'),
                            ),
                          ],
                        ),
                      )
                    : employeesState.employees.isEmpty
                        ? const Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.people, size: 48, color: Colors.grey),
                                SizedBox(height: 16),
                                Text('No employees found'),
                                Text('Add your first employee to get started'),
                              ],
                            ),
                          )
                        : ListView.builder(
                            itemCount: employeesState.employees.length,
                            itemBuilder: (context, index) {
                              final employee = employeesState.employees[index];
                              return EmployeeCard(
                                employee: employee,
                                userRole: userRole,
                              );
                            },
                          ),
          ),
        ],
      ),
    );
  }
}

class EmployeeCard extends StatelessWidget {
  final EmployeeProfile employee;
  final String? userRole;

  const EmployeeCard({
    super.key,
    required this.employee,
    required this.userRole,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.primary,
          child: Text(
            employee.position?.substring(0, 1) ?? 'E',
            style: const TextStyle(color: Colors.white),
          ),
        ),
        title: Text(employee.position ?? 'Employee'),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (employee.department != null)
              Text(employee.department!),
            if (employee.phone != null)
              Text(employee.phone!, style: const TextStyle(fontSize: 12)),
          ],
        ),
        trailing: Chip(
          label: Text(employee.isActive ? 'Active' : 'Inactive'),
          backgroundColor: employee.isActive
              ? Colors.green.withOpacity(0.2)
              : Colors.red.withOpacity(0.2),
          labelStyle: TextStyle(
            color: employee.isActive ? Colors.green : Colors.red,
            fontSize: 12,
          ),
        ),
        onTap: () {
          // TODO: Navigate to employee details screen
          _showEmployeeDetails(context, employee);
        },
      ),
    );
  }

  void _showEmployeeDetails(BuildContext context, EmployeeProfile employee) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => EmployeeDetailsSheet(
        employee: employee,
        userRole: userRole,
      ),
    );
  }
}

class _AttendanceTab extends StatelessWidget {
  const _AttendanceTab();
  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.access_time, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('Attendance Management'),
          Text('Track employee attendance and time records'),
        ],
      ),
    );
  }
}

class _LeaveRequestsTab extends StatelessWidget {
  const _LeaveRequestsTab();
  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.beach_access, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('Leave Requests'),
          Text('Manage employee leave applications'),
        ],
      ),
    );
  }
}

class _PayrollTab extends StatelessWidget {
  const _PayrollTab();
  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.attach_money, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('Payroll Management'),
          Text('Handle employee compensation and benefits'),
        ],
      ),
    );
  }
}

class AddEmployeeDialog extends ConsumerStatefulWidget {
  const AddEmployeeDialog({super.key});

  @override
  ConsumerState<AddEmployeeDialog> createState() => _AddEmployeeDialogState();
}

class _AddEmployeeDialogState extends ConsumerState<AddEmployeeDialog> {
  final _formKey = GlobalKey<FormState>();
  final _userIdController = TextEditingController();
  final _companyIdController = TextEditingController();
  final _departmentController = TextEditingController();
  final _positionController = TextEditingController();
  final _phoneController = TextEditingController();
  DateTime? _hireDate;
  bool _isLoading = false;

  @override
  void dispose() {
    _userIdController.dispose();
    _companyIdController.dispose();
    _departmentController.dispose();
    _positionController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add Employee Profile'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _userIdController,
                decoration: const InputDecoration(
                  labelText: 'User ID',
                  hintText: 'Enter user ID (e.g., 1, 2, 3)',
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return 'User ID is required';
                  }
                  final userId = int.tryParse(value!);
                  if (userId == null) {
                    return 'Please enter a valid user ID';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _companyIdController,
                decoration: const InputDecoration(
                  labelText: 'Company ID',
                  hintText: 'Enter company ID (e.g., 1, 2, 3)',
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return 'Company ID is required';
                  }
                  final companyId = int.tryParse(value!);
                  if (companyId == null) {
                    return 'Please enter a valid company ID';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _departmentController,
                decoration: const InputDecoration(
                  labelText: 'Department',
                  hintText: 'e.g., Engineering, Sales, HR',
                ),
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return 'Department is required';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _positionController,
                decoration: const InputDecoration(
                  labelText: 'Position',
                  hintText: 'e.g., Software Engineer, Manager',
                ),
                validator: (value) {
                  if (value?.isEmpty ?? true) {
                    return 'Position is required';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _phoneController,
                decoration: const InputDecoration(
                  labelText: 'Phone',
                  hintText: '+1 (555) 123-4567',
                ),
                keyboardType: TextInputType.phone,
              ),
              const SizedBox(height: 16),
              InkWell(
                onTap: () async {
                  final date = await showDatePicker(
                    context: context,
                    initialDate: DateTime.now(),
                    firstDate: DateTime(2000),
                    lastDate: DateTime.now(),
                  );
                  if (date != null) {
                    setState(() => _hireDate = date);
                  }
                },
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Hire Date',
                    suffixIcon: Icon(Icons.calendar_today),
                  ),
                  child: Text(
                    _hireDate != null
                        ? '${_hireDate!.month}/${_hireDate!.day}/${_hireDate!.year}'
                        : 'Select hire date',
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _submitForm,
          child: _isLoading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Add Employee'),
        ),
      ],
    );
  }

  void _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final userId = int.parse(_userIdController.text);
      final companyId = int.parse(_companyIdController.text);

      await ref.read(employeesProvider.notifier).createEmployee(
        userId: userId,
        companyId: companyId,
        department: _departmentController.text.isNotEmpty ? _departmentController.text : null,
        position: _positionController.text.isNotEmpty ? _positionController.text : null,
        phone: _phoneController.text.isNotEmpty ? _phoneController.text : null,
        hireDate: _hireDate,
      );

      // Check if there was an error
      final employeesState = ref.read(employeesProvider);
      if (employeesState.error != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${employeesState.error}')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Employee created successfully')),
        );
        Navigator.pop(context);
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

class EmployeeDetailsSheet extends StatelessWidget {
  final EmployeeProfile employee;
  final String? userRole;

  const EmployeeDetailsSheet({
    super.key,
    required this.employee,
    required this.userRole,
  });

  @override
  Widget build(BuildContext context) {
    final canEdit = userRole == 'SuperAdmin' ||
                   userRole == 'CompanyAdmin' ||
                   userRole == 'Manager';

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.6,
      minChildSize: 0.4,
      maxChildSize: 0.9,
      builder: (context, scrollController) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  child: Text(
                    employee.position?.substring(0, 1) ?? 'E',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        employee.position ?? 'Employee',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      if (employee.department != null)
                        Text(
                          employee.department!,
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                    ],
                  ),
                ),
                if (canEdit)
                  IconButton(
                    onPressed: () {
                      // TODO: Show edit dialog
                    },
                    icon: const Icon(Icons.edit),
                  ),
              ],
            ),
            const SizedBox(height: 24),
            const Text(
              'Details',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _DetailRow(
              label: 'Department',
              value: employee.department ?? 'Not specified',
            ),
            _DetailRow(
              label: 'Position',
              value: employee.position ?? 'Not specified',
            ),
            if (employee.phone != null)
              _DetailRow(
                label: 'Phone',
                value: employee.phone!,
              ),
            if (employee.hireDate != null)
              _DetailRow(
                label: 'Hire Date',
                value: '${employee.hireDate!.month}/${employee.hireDate!.day}/${employee.hireDate!.year}',
              ),
            _DetailRow(
              label: 'Status',
              value: employee.isActive ? 'Active' : 'Inactive',
            ),
            const SizedBox(height: 24),
            if (canEdit)
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () {
                        // TODO: Implement edit functionality
                      },
                      child: const Text('Edit Profile'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        // TODO: Implement delete functionality
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                      ),
                      child: const Text('Delete'),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.grey,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontSize: 16),
            ),
          ),
        ],
      ),
    );
  }
}
