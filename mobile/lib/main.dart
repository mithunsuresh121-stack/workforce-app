import 'package:flutter/material.dart';
import 'package:workforce_app/src/app.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // ← Remove ANY await Firebase.initializeApp(), heavy API calls, or SharedPreferences.getInstance() here
  runApp(const ProviderScope(child: WorkforceApp()));
}
