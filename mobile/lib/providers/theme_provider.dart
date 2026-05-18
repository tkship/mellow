import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeNotifier extends Notifier<ThemeMode> {
  static const _key = 'theme_mode';
  SharedPreferences? _prefs;

  Future<SharedPreferences> get _prefsAsync => _prefs != null
      ? Future.value(_prefs!)
      : SharedPreferences.getInstance().then((p) {
          _prefs = p;
          return p;
        });

  @override
  ThemeMode build() {
    _loadTheme();
    return ThemeMode.system;
  }

  Future<void> _loadTheme() async {
    final prefs = await _prefsAsync;
    final value = prefs.getString(_key);
    if (value != null) {
      state = _parseThemeMode(value);
    }
  }

  Future<void> setTheme(ThemeMode mode) async {
    state = mode;
    final prefs = await _prefsAsync;
    await prefs.setString(_key, mode.name);
  }

  Future<void> toggle() async {
    if (state == ThemeMode.dark) {
      await setTheme(ThemeMode.light);
    } else {
      await setTheme(ThemeMode.dark);
    }
  }

  ThemeMode _parseThemeMode(String value) {
    return switch (value) {
      'light' => ThemeMode.light,
      'dark' => ThemeMode.dark,
      _ => ThemeMode.system,
    };
  }
}

final themeProvider = NotifierProvider<ThemeNotifier, ThemeMode>(
  ThemeNotifier.new,
);
