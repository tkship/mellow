import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import 'screens/login_screen.dart';
import 'screens/persona_select_screen.dart';
import 'screens/chat_screen.dart';

class MellowApp extends StatelessWidget {
  const MellowApp({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFFFF7B6C),
      brightness: Brightness.light,
    ).copyWith(
      onPrimary: const Color(0xFF3D2C2C),
      surface: const Color(0xFFFFFBF5),
      surfaceContainerHighest: const Color(0xFFFFF2ED),
    );

    final textTheme = GoogleFonts.poppinsTextTheme().merge(
      GoogleFonts.interTextTheme(),
    ).copyWith(
      headlineLarge: GoogleFonts.poppins(
        fontSize: 30,
        fontWeight: FontWeight.bold,
        letterSpacing: -0.5,
        height: 1.1,
      ),
      headlineMedium: GoogleFonts.poppins(
        fontSize: 24,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.3,
        height: 1.15,
      ),
      headlineSmall: GoogleFonts.poppins(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        height: 1.2,
      ),
      titleLarge: GoogleFonts.poppins(
        fontSize: 18,
        fontWeight: FontWeight.w600,
      ),
      titleMedium: GoogleFonts.poppins(
        fontSize: 16,
        fontWeight: FontWeight.w600,
      ),
      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        height: 1.5,
      ),
      bodyMedium: GoogleFonts.inter(
        fontSize: 14,
        height: 1.5,
      ),
      bodySmall: GoogleFonts.inter(
        fontSize: 12,
        height: 1.4,
      ),
      labelLarge: GoogleFonts.poppins(
        fontSize: 14,
        fontWeight: FontWeight.w600,
      ),
      labelSmall: GoogleFonts.inter(
        fontSize: 11,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.3,
      ),
    );

    return MaterialApp(
      title: 'Mellow',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: colorScheme,
        useMaterial3: true,
        textTheme: textTheme,

        // --- Buttons ---
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            shape: const StadiumBorder(),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            shape: const StadiumBorder(),
          ),
        ),

        // --- Input Fields ---
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 14,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
            borderSide: BorderSide.none,
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
            borderSide: BorderSide(
              color: colorScheme.primary,
              width: 2,
            ),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          focusedErrorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          hintStyle: GoogleFonts.inter(
            color: colorScheme.onSurface.withOpacity(0.4),
          ),
        ),

        // --- Cards ---
        cardTheme: CardThemeData(
          elevation: 2,
          surfaceTintColor: colorScheme.surfaceTint,
          shadowColor: colorScheme.primary.withOpacity(0.10),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),

        // --- Dialogs ---
        dialogTheme: DialogThemeData(
          elevation: 8,
          shadowColor: colorScheme.shadow.withOpacity(0.18),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),

        // --- Chips ---
        chipTheme: ChipThemeData(
          shape: const StadiumBorder(),
          elevation: 1,
          shadowColor: colorScheme.primary.withOpacity(0.06),
        ),

        // --- AppBar ---
        appBarTheme: AppBarTheme(
          surfaceTintColor: colorScheme.surfaceTint,
          scrolledUnderElevation: 0,
          elevation: 0,
          shadowColor: Colors.transparent,
          centerTitle: false,
        ),

        // --- SnackBar ---
        snackBarTheme: SnackBarThemeData(
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          elevation: 4,
        ),

        // --- Navigation ---
        navigationBarTheme: NavigationBarThemeData(
          elevation: 0,
          indicatorShape: const StadiumBorder(),
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        ),

        // --- Page Transitions ---
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: {
            TargetPlatform.android: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.iOS: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.linux: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.macOS: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.windows: FadeUpwardsPageTransitionsBuilder(),
          },
        ),
      ),
      home: Consumer<AuthProvider>(
        builder: (_, auth, __) {
          if (!auth.isLoggedIn) return const LoginScreen();
          if (auth.currentPersona == null) return const PersonaSelectScreen();
          return const ChatScreen();
        },
      ),
    );
  }
}
