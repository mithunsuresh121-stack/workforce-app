import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

enum AppTheme { light, dark, system }

class ThemeState {
  final AppTheme theme;
  final ThemeData themeData;

  ThemeState({
    required this.theme,
    required this.themeData,
  });

  ThemeState copyWith({
    AppTheme? theme,
    ThemeData? themeData,
  }) {
    return ThemeState(
      theme: theme ?? this.theme,
      themeData: themeData ?? this.themeData,
    );
  }
}

class ThemeNotifier extends StateNotifier<ThemeState> {
  ThemeNotifier() : super(_getInitialState());

  static ThemeState _getInitialState() {
    return ThemeState(
      theme: AppTheme.system,
      themeData: _getThemeData(AppTheme.system),
    );
  }

  static ThemeData _getThemeData(AppTheme theme) {
    final brightness = theme == AppTheme.dark 
      ? Brightness.dark 
      : theme == AppTheme.light 
        ? Brightness.light 
        : WidgetsBinding.instance.platformDispatcher.platformBrightness;

    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.indigo,
        brightness: brightness,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: brightness == Brightness.dark 
          ? Colors.grey[900] 
          : Colors.white,
        foregroundColor: brightness == Brightness.dark 
          ? Colors.white 
          : Colors.black,
      ),
      cardTheme: CardThemeData(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        filled: true,
        fillColor: brightness == Brightness.dark 
          ? Colors.grey[800] 
          : Colors.grey[50],
      ),
    );
  }

  Future<void> setTheme(AppTheme theme) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('theme', theme.toString());
    
    state = state.copyWith(
      theme: theme,
      themeData: _getThemeData(theme),
    );
  }

  Future<void> loadTheme() async {
    final prefs = await SharedPreferences.getInstance();
    final themeString = prefs.getString('theme');
    
    if (themeString != null) {
      final theme = AppTheme.values.firstWhere(
        (t) => t.toString() == themeString,
        orElse: () => AppTheme.system,
      );
      
      state = state.copyWith(
        theme: theme,
        themeData: _getThemeData(theme),
      );
    }
  }
}

final themeProvider = StateNotifierProvider<ThemeNotifier, ThemeState>((ref) {
  return ThemeNotifier();
});
