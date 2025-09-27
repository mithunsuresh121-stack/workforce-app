import 'package:flutter/material.dart';
import 'package:music_app/src/app.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(
    const ProviderScope(
      child: MusicApp(),
    ),
  );
}
