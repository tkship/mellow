import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Mellow 字体系统：Lato（正文）+ Quicksand（标签/按钮）
class MellowTypography {
  MellowTypography._();

  static TextStyle get displayLarge =>
      GoogleFonts.quicksand(fontSize: 32, fontWeight: FontWeight.w700);

  static TextStyle get displayMedium =>
      GoogleFonts.quicksand(fontSize: 28, fontWeight: FontWeight.w700);

  static TextStyle get headline =>
      GoogleFonts.quicksand(fontSize: 24, fontWeight: FontWeight.w600);

  static TextStyle get title =>
      GoogleFonts.lato(fontSize: 20, fontWeight: FontWeight.w600);

  static TextStyle get subtitle =>
      GoogleFonts.lato(fontSize: 16, fontWeight: FontWeight.w500);

  static TextStyle get body =>
      GoogleFonts.lato(fontSize: 15, fontWeight: FontWeight.w400);

  static TextStyle get bodySmall =>
      GoogleFonts.lato(fontSize: 13, fontWeight: FontWeight.w400);

  static TextStyle get label =>
      GoogleFonts.quicksand(fontSize: 14, fontWeight: FontWeight.w600);

  static TextStyle get button =>
      GoogleFonts.quicksand(fontSize: 15, fontWeight: FontWeight.w700);
}
