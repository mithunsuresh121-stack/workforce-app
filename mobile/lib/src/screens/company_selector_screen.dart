import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/providers/auth_provider.dart';
import 'package:workforce_app/src/screens/dashboard_screen.dart';

class CompanySelectorScreen extends ConsumerWidget {
  const CompanySelectorScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Select Company'),
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Choose a company to continue:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            if (authState.userCompanies != null && authState.userCompanies!.isNotEmpty)
              Expanded(
                child: ListView.builder(
                  itemCount: authState.userCompanies!.length,
                  itemBuilder: (context, index) {
                    final company = authState.userCompanies![index];
                    return Card(
                      child: ListTile(
                        leading: const Icon(Icons.business),
                        title: Text(company['name'] ?? 'Unknown Company'),
                        subtitle: Text('ID: ${company['id']}'),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () async {
                          final authNotifier = ref.read(authProvider.notifier);
                          await authNotifier.switchCompany(company['id']);
                          if (context.mounted) {
                            Navigator.of(context).pushReplacement(
                              MaterialPageRoute(builder: (context) => const DashboardScreen()),
                            );
                          }
                        },
                      ),
                    );
                  },
                ),
              )
            else
              const Expanded(
                child: Center(
                  child: Text('No companies available'),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
