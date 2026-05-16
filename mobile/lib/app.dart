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
    final textTheme = GoogleFonts.poppinsTextTheme().merge(GoogleFonts.interTextTheme());

    return MaterialApp(
      title: 'Mellow',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: cs,
        useMaterial3: true,
        textTheme: textTheme,
        scaffoldBackgroundColor: cs.surface,
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
