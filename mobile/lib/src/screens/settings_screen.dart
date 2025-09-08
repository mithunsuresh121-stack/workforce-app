// ignore_for_file: deprecated_member_use

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/providers/auth_provider.dart';
import 'package:workforce_app/src/providers/theme_provider.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});
  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    final themeState = ref.watch(themeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Theme',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            ListTile(
              title: const Text('Light Mode'),
              leading: Radio<AppTheme>(
                value: AppTheme.light,
                groupValue: themeState.theme,
                onChanged: (value) {
                  if (value != null) {
                    ref.read(themeProvider.notifier).setTheme(value);
                  }
                },
              ),
            ),
            ListTile(
              title: const Text('Dark Mode'),
              leading: Radio<AppTheme>(
                value: AppTheme.dark,
                groupValue: themeState.theme,
                onChanged: (value) {
                  if (value != null) {
                    ref.read(themeProvider.notifier).setTheme(value);
                  }
                },
              ),
            ),
            ListTile(
              title: const Text('System Default'),
              leading: Radio<AppTheme>(
                value: AppTheme.system,
                groupValue: themeState.theme,
                onChanged: (value) {
                  if (value != null) {
                    ref.read(themeProvider.notifier).setTheme(value);
                  }
                },
              ),
            ),
            const Divider(),
            const SizedBox(height: 16),
            Text(
              'Account Settings',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            ListTile(
              title: const Text('Change Password'),
              onTap: () {
                // TODO: Implement change password functionality
              },
            ),
            ListTile(
              title: const Text('Logout'),
              onTap: () {
                ref.read(authProvider.notifier).logout();
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }
}
