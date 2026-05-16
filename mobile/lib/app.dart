import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

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
      theme: ThemeData(colorScheme: cs, useMaterial3: true, textTheme: textTheme),
      home: const Scaffold(body: Center(child: Text('UI pending'))),
    );
  }
}
