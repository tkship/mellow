import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import 'screens/login_screen.dart';
import 'screens/persona_select_screen.dart';
import 'screens/chat_screen.dart';

class MellowApp extends StatelessWidget {
  const MellowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mellow',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6C63FF),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
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
