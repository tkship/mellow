import 'package:flutter/material.dart';

/// Mellow 间距、圆角、阴影令牌
class MellowSpacing {
  MellowSpacing._();

  // ── 间距 ──
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;

  // ── 圆角 ──
  static const double radiusSm = 8;
  static const double radiusMd = 12;
  static const double radiusLg = 16;
  static const double radiusXl = 24;
  static const double radiusFull = 999;

  // ── 消息气泡 ──
  static const double bubbleRadius = 16;
  static const BorderRadius bubbleAi = BorderRadius.only(
    topLeft: Radius.circular(4),
    topRight: Radius.circular(bubbleRadius),
    bottomLeft: Radius.circular(bubbleRadius),
    bottomRight: Radius.circular(bubbleRadius),
  );
  static const BorderRadius bubbleUser = BorderRadius.only(
    topLeft: Radius.circular(bubbleRadius),
    topRight: Radius.circular(4),
    bottomLeft: Radius.circular(bubbleRadius),
    bottomRight: Radius.circular(bubbleRadius),
  );

  // ── 阴影 ──
  static List<BoxShadow> get shadowCard => [
        BoxShadow(
          color: Colors.black.withAlpha(10),
          blurRadius: 8,
          offset: const Offset(0, 2),
        ),
      ];

  static List<BoxShadow> get shadowBubble => [
        BoxShadow(
          color: Colors.black.withAlpha(8),
          blurRadius: 4,
          offset: const Offset(0, 1),
        ),
        BoxShadow(
          color: Colors.black.withAlpha(6),
          blurRadius: 8,
          offset: const Offset(0, 4),
        ),
      ];
}
