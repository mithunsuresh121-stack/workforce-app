import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/providers/companies_provider.dart';

class CompanyManagementScreen extends ConsumerStatefulWidget {
  const CompanyManagementScreen({super.key});
  @override
  ConsumerState<CompanyManagementScreen> createState() => _CompanyManagementScreenState();
}

class _CompanyManagementScreenState extends ConsumerState<CompanyManagementScreen> {
  final TextEditingController _companyNameController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Fetch companies when the screen is first loaded
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(companiesProvider.notifier).fetchCompanies();
    });
  }

  @override
  Widget build(BuildContext context) {
    final companiesState = ref.watch(companiesProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Company Management'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _companyNameController,
              decoration: const InputDecoration(
                labelText: 'Company Name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                final companyName = _companyNameController.text.trim();
                if (companyName.isNotEmpty) {
                  ref.read(companiesProvider.notifier).createCompany(context, companyName);
                  _companyNameController.clear();
                }
              },
              child: const Text('Add Company'),
            ),
            // Error Display
            if (companiesState.error != null)
              Container(
                padding: const EdgeInsets.all(8.0),
                color: Colors.red[100],
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        companiesState.error!,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () {
                        ref.read(companiesProvider.notifier).clearError();
                      },
                    ),
                  ],
                ),
              ),
            
            // Loading Indicator
            if (companiesState.isLoading)
              const Center(child: CircularProgressIndicator()),
              
            const SizedBox(height: 16),
            
            // Companies List
            Expanded(
              child: companiesState.companies.isEmpty && !companiesState.isLoading
                  ? const Center(
                      child: Text(
                        'No companies found',
                        style: TextStyle(fontSize: 18, color: Colors.grey),
                      ),
                    )
                  : ListView.builder(
                      itemCount: companiesState.companies.length,
                      itemBuilder: (context, index) {
                        final company = companiesState.companies[index];
                        return ListTile(
                          title: Text(company.name),
                          subtitle: Text('ID: ${company.id}'),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete, color: Colors.red),
                            onPressed: () {
                              ref.read(companiesProvider.notifier).deleteCompany(context, company.id);
                            },
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
