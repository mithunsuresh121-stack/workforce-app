import 'package:flutter/material.dart';
import 'package:workforce_app/src/app.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  try {
    runApp(
      const ProviderScope(
        child: WorkforceApp(),
      ),
    );
  } catch (e) {
    // Removed print statement
  } // Closing brace added here
}
