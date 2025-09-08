import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ReportsScreen extends ConsumerStatefulWidget {
  const ReportsScreen({super.key});
  @override
  ConsumerState<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends ConsumerState<ReportsScreen> {
  int _selectedReportType = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Reports & Analytics'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Analytics Dashboard',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            
            // Report type selector
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _ReportTypeChip(
                    key: const Key('report_performance'),
                    label: 'Performance',
                    icon: Icons.assessment,
                    isSelected: _selectedReportType == 0,
                    onTap: () => setState(() => _selectedReportType = 0),
                  ),
                  const SizedBox(width: 8),
                  _ReportTypeChip(
                    key: const Key('report_attendance'),
                    label: 'Attendance',
                    icon: Icons.access_time,
                    isSelected: _selectedReportType == 1,
                    onTap: () => setState(() => _selectedReportType = 1),
                  ),
                  const SizedBox(width: 8),
                  _ReportTypeChip(
                    key: const Key('report_payroll'),
                    label: 'Payroll',
                    icon: Icons.attach_money,
                    isSelected: _selectedReportType == 2,
                    onTap: () => setState(() => _selectedReportType = 2),
                  ),
                  const SizedBox(width: 8),
                  _ReportTypeChip(
                    key: const Key('report_tasks'),
                    label: 'Tasks',
                    icon: Icons.task,
                    isSelected: _selectedReportType == 3,
                    onTap: () => setState(() => _selectedReportType = 3),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Report content based on selection
            Expanded(
              child: IndexedStack(
                index: _selectedReportType,
                children: const [
                  _PerformanceReports(),
                  _AttendanceReports(),
                  _PayrollReports(),
                  _TaskReports(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ReportTypeChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _ReportTypeChip({
    super.key,
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return FilterChip(
      label: Text(label),
      avatar: Icon(icon, size: 16),
      selected: isSelected,
      onSelected: (_) => onTap(),
      showCheckmark: false,
        backgroundColor: isSelected 
        ? Theme.of(context).colorScheme.primary.withValues(alpha: 25) // 0.1 opacity equivalent
        : null,
      labelStyle: TextStyle(
        color: isSelected 
          ? Theme.of(context).colorScheme.primary
          : null,
      ),
    );
  }
}

class _PerformanceReports extends StatelessWidget {
  const _PerformanceReports();

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        _MetricCard(
          key: const Key('metric_overall_performance'),
          title: 'Overall Performance Score',
          value: '87%',
          trend: '+5%',
          icon: Icons.trending_up,
          color: Colors.green,
        ),
        _MetricCard(
          key: const Key('metric_task_completion'),
          title: 'Task Completion Rate',
          value: '92%',
          trend: '+3%',
          icon: Icons.trending_up,
          color: Colors.green,
        ),
        _MetricCard(
          key: const Key('metric_response_time'),
          title: 'Average Response Time',
          value: '2.3h',
          trend: '-0.5h',
          icon: Icons.trending_down,
          color: Colors.red,
        ),
        const SizedBox(height: 16),
        Text(
          'Top Performers',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        _EmployeePerformanceRow(key: const Key('perf_john_smith'), name: 'John Smith', score: '95%', department: 'Operations'),
        _EmployeePerformanceRow(key: const Key('perf_sarah_johnson'), name: 'Sarah Johnson', score: '92%', department: 'IT'),
        _EmployeePerformanceRow(key: const Key('perf_emily_davis'), name: 'Emily Davis', score: '89%', department: 'Finance'),
      ],
    );
  }
}

class _AttendanceReports extends StatelessWidget {
  const _AttendanceReports();

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        _MetricCard(
          key: const Key('metric_attendance_rate'),
          title: 'Overall Attendance Rate',
          value: '96%',
          trend: '+2%',
          icon: Icons.trending_up,
          color: Colors.green,
        ),
        _MetricCard(
          key: const Key('metric_late_arrivals'),
          title: 'Average Late Arrivals',
          value: '1.2',
          trend: '-0.3',
          icon: Icons.trending_down,
          color: Colors.red,
        ),
        _MetricCard(
          key: const Key('metric_leave_utilization'),
          title: 'Leave Utilization',
          value: '65%',
          trend: '+8%',
          icon: Icons.trending_up,
          color: Colors.orange,
        ),
        const SizedBox(height: 16),
        Text(
          'Attendance Summary',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        _AttendanceSummaryRow(key: const Key('attendance_jan'), month: 'January', rate: '98%', late: 2),
        _AttendanceSummaryRow(key: const Key('attendance_feb'), month: 'February', rate: '95%', late: 5),
        _AttendanceSummaryRow(key: const Key('attendance_mar'), month: 'March', rate: '96%', late: 3),
      ],
    );
  }
}

class _PayrollReports extends StatelessWidget {
  const _PayrollReports();

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        _MetricCard(
          key: const Key('metric_payroll_cost'),
          title: 'Total Payroll Cost',
          value: '\$42,500',
          trend: '+5%',
          icon: Icons.trending_up,
          color: Colors.blue,
        ),
        _MetricCard(
          key: const Key('metric_avg_salary'),
          title: 'Average Salary',
          value: '\$3,200',
          trend: '+3%',
          icon: Icons.trending_up,
          color: Colors.green,
        ),
        _MetricCard(
          key: const Key('metric_overtime_costs'),
          title: 'Overtime Costs',
          value: '\$2,800',
          trend: '-12%',
          icon: Icons.trending_down,
          color: Colors.red,
        ),
        const SizedBox(height: 16),
        Text(
          'Payroll Distribution',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        _PayrollDistributionRow(key: const Key('payroll_it'), department: 'IT', amount: '\$15,200', percentage: '36%'),
        _PayrollDistributionRow(key: const Key('payroll_operations'), department: 'Operations', amount: '\$12,800', percentage: '30%'),
        _PayrollDistributionRow(key: const Key('payroll_finance'), department: 'Finance', amount: '\$8,500', percentage: '20%'),
        _PayrollDistributionRow(key: const Key('payroll_hr'), department: 'HR', amount: '\$6,000', percentage: '14%'),
      ],
    );
  }
}

class _TaskReports extends StatelessWidget {
  const _TaskReports();

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        _MetricCard(
          key: const Key('metric_total_tasks'),
          title: 'Total Tasks Completed',
          value: '156',
          trend: '+24',
          icon: Icons.trending_up,
          color: Colors.green,
        ),
        _MetricCard(
          key: const Key('metric_avg_completion'),
          title: 'Average Completion Time',
          value: '2.8 days',
          trend: '-0.5',
          icon: Icons.trending_down,
          color: Colors.red,
        ),
        _MetricCard(
          key: const Key('metric_task_success'),
          title: 'Task Success Rate',
          value: '94%',
          trend: '+3%',
          icon: Icons.trending_up,
          color: Colors.green,
        ),
        const SizedBox(height: 16),
        Text(
          'Task Status Overview',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        _TaskStatusRow(key: const Key('task_completed'), status: 'Completed', count: 156, color: Colors.green),
        _TaskStatusRow(key: const Key('task_in_progress'), status: 'In Progress', count: 42, color: Colors.blue),
        _TaskStatusRow(key: const Key('task_pending'), status: 'Pending', count: 28, color: Colors.orange),
        _TaskStatusRow(key: const Key('task_overdue'), status: 'Overdue', count: 12, color: Colors.red),
      ],
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final String trend;
  final IconData icon;
  final Color color;

  const _MetricCard({
    super.key,
    required this.title,
    required this.value,
    required this.trend,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    value,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            Column(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(height: 4),
                Text(
                  trend,
                  style: TextStyle(color: color, fontSize: 12),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _EmployeePerformanceRow extends StatelessWidget {
  final String name;
  final String score;
  final String department;

  const _EmployeePerformanceRow({
    super.key,
    required this.name,
    required this.score,
    required this.department,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: Theme.of(context).colorScheme.primary,
        child: Text(
          name.substring(0, 1),
          style: const TextStyle(color: Colors.white),
        ),
      ),
      title: Text(name),
      subtitle: Text(department),
      trailing: Chip(
        label: Text(score),
        backgroundColor: Colors.green.withValues(alpha: 51), // 0.2 opacity equivalent
        labelStyle: const TextStyle(color: Colors.green),
      ),
    );
  }
}

class _AttendanceSummaryRow extends StatelessWidget {
  final String month;
  final String rate;
  final int late;

  const _AttendanceSummaryRow({
    super.key,
    required this.month,
    required this.rate,
    required this.late,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(month),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Chip(
            label: Text(rate),
            backgroundColor: Colors.green.withValues(alpha: 51), // 0.2 opacity equivalent
            labelStyle: const TextStyle(color: Colors.green),
          ),
          const SizedBox(width: 8),
          Chip(
            label: Text('$late late'),
        backgroundColor: Colors.orange.withValues(alpha: 51), // 0.2 opacity equivalent
            labelStyle: const TextStyle(color: Colors.orange),
          ),
        ],
      ),
    );
  }
}

class _PayrollDistributionRow extends StatelessWidget {
  final String department;
  final String amount;
  final String percentage;

  const _PayrollDistributionRow({
    super.key,
    required this.department,
    required this.amount,
    required this.percentage,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(department),
      trailing: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(amount, style: const TextStyle(fontWeight: FontWeight.bold)),
          Text(percentage, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        ],
      ),
    );
  }
}

class _TaskStatusRow extends StatelessWidget {
  final String status;
  final int count;
  final Color color;

  const _TaskStatusRow({
    super.key,
    required this.status,
    required this.count,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(status),
      trailing: Chip(
        label: Text(count.toString()),
        backgroundColor: color.withValues(alpha: 51), // 0.2 opacity equivalent
        labelStyle: TextStyle(color: color),
      ),
    );
  }
}
