import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class MellowApp extends StatelessWidget {
  const MellowApp({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = ColorScheme.fromSeed(
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
        colorScheme: colorScheme,
        useMaterial3: true,
        textTheme: textTheme,
        scaffoldBackgroundColor: colorScheme.surface,
      ),
      home: const _Placeholder(),
    );
  }
}

class _Placeholder extends StatelessWidget {
  const _Placeholder();
  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('UI rebuild pending...')),
    );
  }
}
