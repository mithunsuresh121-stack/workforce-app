import 'package:flutter/material.dart';
import 'package:workforce_app/src/providers/auth_provider.dart';
import 'package:workforce_app/src/providers/tasks_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    // Fetch tasks when the screen is initialized
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(tasksProvider.notifier).fetchTasks();
    });
  }

  @override
  Widget build(BuildContext context) {
    final tasksState = ref.watch(tasksProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome message
            _WelcomeSection(),
            const SizedBox(height: 24),
            
            // Quick Stats
            Text(
              'Quick Stats',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            _QuickStatsGrid(),
            const SizedBox(height: 24),
            
            // Recent Activities
            Text(
              'Recent Activities',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            _RecentActivitiesList(),
            const SizedBox(height: 24),
            
            // Upcoming Tasks
            Text(
              'Upcoming Deadlines',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            if (tasksState.isLoading)
              const Center(child: CircularProgressIndicator())
            else if (tasksState.error != null)
              Center(
                child: Text(
                  'Error: ${tasksState.error}',
                  style: TextStyle(color: Colors.red),
                ),
              )
            else
              _UpcomingTasksList(),
          ],
        ),
      ),
    );
  }
}

// Welcome Section
class _WelcomeSection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            // Logo placeholder
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.business_center, size: 40, color: Colors.grey),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome back!',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    authState.email ?? 'User',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Company ID: ${authState.companyId ?? 'N/A'}',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Quick Stats Grid
class _QuickStatsGrid extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasksState = ref.watch(tasksProvider);
    
    final openTasks = tasksState.tasks
        .where((task) => task.status != 'completed')
        .length;

    final highPriorityTasks = tasksState.tasks
        .where((task) => (task.priority == 'High' || task.priority == null) && task.status != 'completed')
        .length;

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        _KpiCard(
          title: "Active Employees",
          value: "42",
          icon: Icons.people,
          color: Colors.blue,
        ),
        _KpiCard(
          title: "Open Tasks",
          value: openTasks.toString(),
          icon: Icons.task,
          color: Colors.orange,
        ),
        _KpiCard(
          title: "High Priority",
          value: highPriorityTasks.toString(),
          icon: Icons.warning,
          color: Colors.red,
        ),
        _KpiCard(
          title: "On-time Rate",
          value: "96%",
          icon: Icons.timer,
          color: Colors.purple,
        ),
        _KpiCard(
          title: "New Messages",
          value: "5",
          icon: Icons.email,
          color: Colors.red,
        ),
        _KpiCard(
          title: "Projects",
          value: "8",
          icon: Icons.work,
          color: Colors.teal,
        ),
      ],
    );
  }
}

// Recent Activities List
class _RecentActivitiesList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _ActivityItem(
              icon: Icons.task,
              title: 'Task Completed',
              description: 'John completed "Website Redesign"',
              time: '2 hours ago',
              color: Colors.green,
            ),
            _ActivityItem(
              icon: Icons.person_add,
              title: 'New Employee',
              description: 'Sarah Johnson joined the team',
              time: '4 hours ago',
              color: Colors.blue,
            ),
            _ActivityItem(
              icon: Icons.calendar_today,
              title: 'Leave Request',
              description: 'Mike requested leave for tomorrow',
              time: '6 hours ago',
              color: Colors.orange,
            ),
            _ActivityItem(
              icon: Icons.chat,
              title: 'New Message',
              description: 'New message from client',
              time: '8 hours ago',
              color: Colors.purple,
            ),
          ],
        ),
      ),
    );
  }
}

// Upcoming Tasks List
class _UpcomingTasksList extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasksState = ref.watch(tasksProvider);
    
    // Fetch tasks when widget is built
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(tasksProvider.notifier).fetchTasks();
    });

    if (tasksState.isLoading) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Center(
            child: CircularProgressIndicator(),
          ),
        ),
      );
    }

    if (tasksState.error != null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(Icons.error_outline, color: Colors.red, size: 48),
              SizedBox(height: 8),
              Text(
                'Error loading tasks',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              SizedBox(height: 4),
              Text(
                tasksState.error!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    final upcomingTasks = tasksState.tasks
        .where((task) => task.dueDate != null && 
            task.dueDate!.isAfter(DateTime.now().subtract(Duration(days: 1))))
        .toList()
      ..sort((a, b) => a.dueDate!.compareTo(b.dueDate!));

    if (upcomingTasks.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(Icons.calendar_today, color: Colors.grey, size: 48),
              SizedBox(height: 8),
              Text(
                'No upcoming tasks',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              SizedBox(height: 4),
              Text(
                'All caught up!',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: upcomingTasks.take(3).map((task) => _TaskItem(
            title: task.title,
            dueDate: _formatDueDate(task.dueDate!),
            priority: task.priority,
            assignee: task.assignee ?? 'Unassigned',
          )).toList(),
        ),
      ),
    );
  }

  String _formatDueDate(DateTime dueDate) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final tomorrow = today.add(Duration(days: 1));
    
    if (dueDate.isBefore(today)) {
      return 'Overdue: ${dueDate.toString().split(' ')[0]}';
    } else if (dueDate.isAtSameMomentAs(today)) {
      return 'Today';
    } else if (dueDate.isAtSameMomentAs(tomorrow)) {
      return 'Tomorrow';
    } else {
      return dueDate.toString().split(' ')[0];
    }
  }
}

// KPI Card
class _KpiCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _KpiCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1), // Updated to withValues
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: color, size: 20),
                ),
                const Spacer(),
                Text(
                  value,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Activity Item
class _ActivityItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final String time;
  final Color color;

  const _ActivityItem({
    required this.icon,
    required this.title,
    required this.description,
    required this.time,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1), // Updated to withValues
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title, style: Theme.of(context).textTheme.bodyLarge),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(description),
          const SizedBox(height: 2),
          Text(
            time,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}

// Task Item
class _TaskItem extends StatelessWidget {
  final String title;
  final String dueDate;
  final String? priority; // Make priority nullable
  final String assignee;

  const _TaskItem({
    required this.title,
    required this.dueDate,
    required this.priority,
    required this.assignee,
  });

  @override
  Widget build(BuildContext context) {
    Color priorityColor = (priority == 'High' || priority == null)
      ? Colors.red 
      : priority == 'Medium' 
        ? Colors.orange 
        : Colors.green;

    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: priorityColor.withOpacity(0.1), // Updated to withValues
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          Icons.circle,
          color: priorityColor,
          size: 12,
        ),
      ),
      title: Text(title, style: Theme.of(context).textTheme.bodyLarge),
      subtitle: Text('Assigned to: $assignee'),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            dueDate,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 2),
          Text(
            priority ?? 'N/A',
            style: TextStyle(
              color: priorityColor,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
