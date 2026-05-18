import 'package:flutter/material.dart';

/// Mellow 品牌色令牌 — Light / Dark 双主题
class MellowColors {
  MellowColors._();

  // ── 品牌主色 ──
  static const Color brandGreen = Color(0xFF5BC91A);
  static const Color brandOrange = Color(0xFFF09433);

  // ── Light 主题 ──
  static const Color lightBg = Color(0xFFFAFAFA);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightText = Color(0xFF1A1A2E);
  static const Color lightTextSecondary = Color(0xFF6B7280);
  static const Color lightBorder = Color(0xFFE5E7EB);

  // ── Dark 主题 ──
  static const Color darkBg = Color(0xFF0D1117);
  static const Color darkSurface = Color(0xFF161B22);
  static const Color darkText = Color(0xFFE6EDF3);
  static const Color darkTextSecondary = Color(0xFF8B949E);
  static const Color darkBorder = Color(0xFF30363D);

  // ── 语义色 ──
  static const Color error = Color(0xFFEF4444);
  static const Color success = brandGreen;
  static const Color warning = brandOrange;
  static const Color favoriteGold = Color(0xFFF59E0B);
  static const Color starBlue = Color(0xFF3B82F6);

  /// Returns theme-aware secondary text color
  static Color textSecondary(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? darkTextSecondary
          : lightTextSecondary;

  /// Returns theme-aware border color
  static Color border(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? darkBorder
          : lightBorder;
}
