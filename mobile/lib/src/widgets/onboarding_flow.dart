import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/providers/auth_provider.dart';
import 'package:workforce_app/src/screens/company_creation_screen.dart';
import 'package:workforce_app/src/screens/company_selector_screen.dart';

class OnboardingFlow extends ConsumerWidget {
  const OnboardingFlow({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    // Show loading while checking companies
    if (authState.isLoading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    // If user has no companies, show company creation
    if (authState.userCompanies == null || authState.userCompanies!.isEmpty) {
      return const CompanyCreationScreen();
    }

    // If user has exactly one company, auto-select and go to dashboard
    if (authState.userCompanies!.length == 1) {
      final company = authState.userCompanies!.first;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        final authNotifier = ref.read(authProvider.notifier);
        authNotifier.switchCompany(company['id']);
        Navigator.of(context).pushReplacementNamed('/dashboard');
      });
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    // If user has multiple companies, show selector
    return const CompanySelectorScreen();
  }
}
