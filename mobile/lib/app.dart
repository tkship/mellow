import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import 'screens/chat_screen.dart';
import 'screens/login_screen.dart';
import 'screens/persona_select_screen.dart';

class MellowApp extends StatelessWidget {
  const MellowApp({super.key});

  @override
  Widget build(BuildContext context) {
    final cs = ColorScheme.fromSeed(
      seedColor: const Color(0xFFFF7B6C),
      brightness: Brightness.light,
    );

    final textTheme = GoogleFonts.poppinsTextTheme().merge(
      GoogleFonts.interTextTheme(),
    );

    return MaterialApp(
      title: 'Mellow',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: cs,
        useMaterial3: true,
        textTheme: textTheme,
        scaffoldBackgroundColor: cs.surface,

        // ── Inputs: underline style, no borders ──
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: cs.surfaceContainerHighest.withAlpha(100),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 20,
            vertical: 18,
          ),
          border: UnderlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          enabledBorder: UnderlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          focusedBorder: UnderlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide(color: cs.primary, width: 2),
          ),
          errorBorder: UnderlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide(color: cs.error, width: 1),
          ),
        ),

        // ── Buttons: pill-shaped, generous ──
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            elevation: 0,
            minimumSize: const Size(double.infinity, 56),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(28),
            ),
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.5,
            ),
          ),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: cs.primary,
            textStyle: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ),

        // ── Dialog: slide from top ──
        dialogTheme: DialogThemeData(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(28),
          ),
        ),

        // ── SnackBar: floating pill ──
        snackBarTheme: SnackBarThemeData(
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),

      // ── Routing ──
      home: Consumer<AuthProvider>(
        builder: (_, auth, __) {
          if (!auth.isLoggedIn) return const LoginScreen();
          if (auth.currentPersona == null) {
            return const PersonaSelectScreen();
          }
          return const ChatScreen();
        },
      ),
    );
  }
}
