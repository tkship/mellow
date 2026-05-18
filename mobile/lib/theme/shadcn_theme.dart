import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import 'colors.dart';

ShadThemeData _buildTheme({
  required Brightness brightness,
  required Color background,
  required Color foreground,
  required Color card,
  required Color cardForeground,
  required Color popover,
  required Color popoverForeground,
  required Color muted,
  required Color mutedForeground,
  required Color border,
  required Color input,
  required Color ring,
}) {
  return ShadThemeData(
    brightness: brightness,
    colorScheme: ShadColorScheme(
      background: background,
      foreground: foreground,
      card: card,
      cardForeground: cardForeground,
      popover: popover,
      popoverForeground: popoverForeground,
      primary: MellowColors.brandGreen,
      primaryForeground: Colors.white,
      secondary: MellowColors.brandOrange,
      secondaryForeground: Colors.white,
      muted: muted,
      mutedForeground: mutedForeground,
      accent: MellowColors.brandGreen,
      accentForeground: Colors.white,
      destructive: MellowColors.error,
      destructiveForeground: Colors.white,
      border: border,
      input: input,
      ring: ring,
      selection: MellowColors.brandGreen.withAlpha(40),
    ),
    radius: const BorderRadius.all(Radius.circular(12)),
  );
}

final mellowLightTheme = _buildTheme(
  brightness: Brightness.light,
  background: MellowColors.lightBg,
  foreground: MellowColors.lightText,
  card: MellowColors.lightSurface,
  cardForeground: MellowColors.lightText,
  popover: MellowColors.lightSurface,
  popoverForeground: MellowColors.lightText,
  muted: const Color(0xFFF3F4F6),
  mutedForeground: MellowColors.lightTextSecondary,
  border: MellowColors.lightBorder,
  input: MellowColors.lightBorder,
  ring: MellowColors.brandGreen,
);

final mellowDarkTheme = _buildTheme(
  brightness: Brightness.dark,
  background: MellowColors.darkBg,
  foreground: MellowColors.darkText,
  card: MellowColors.darkSurface,
  cardForeground: MellowColors.darkText,
  popover: MellowColors.darkSurface,
  popoverForeground: MellowColors.darkText,
  muted: const Color(0xFF21262D),
  mutedForeground: MellowColors.darkTextSecondary,
  border: MellowColors.darkBorder,
  input: MellowColors.darkBorder,
  ring: MellowColors.brandGreen,
);
