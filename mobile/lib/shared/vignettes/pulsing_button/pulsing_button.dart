import 'package:flutter/material.dart';

import 'package:mellow/shared/vignettes/pulsing_button/circle_painter.dart';

/// A button with an animated pulsing ring effect.
///
/// Displays an icon button surrounded by a fading, expanding circle animation.
/// The [color], [size], and [icon] are fully customizable.
///
/// Default color is Mellow brand green (#5BC91A).
class PulsingButton extends StatefulWidget {
  /// Called when the button is tapped.
  final VoidCallback onPressed;

  /// The icon displayed inside the button.
  final IconData icon;

  /// The primary color of the button and pulse ring.
  ///
  /// Defaults to Mellow brand green (#5BC91A).
  final Color color;

  /// The diameter of the button in logical pixels.
  ///
  /// Defaults to 56.0.
  final double size;

  /// The color of the tap splash and hover effects.
  ///
  /// If not provided, a darkened variant of [color] is used.
  final Color? splashColor;

  const PulsingButton({
    super.key,
    required this.onPressed,
    required this.icon,
    this.color = const Color(0xFF5BC91A),
    this.size = 56.0,
    this.splashColor,
  });

  @override
  State<PulsingButton> createState() => _PulsingButtonState();
}

class _PulsingButtonState extends State<PulsingButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _btnAnimController = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1200),
  )..repeat();
  late final CurvedAnimation _btnAnim = CurvedAnimation(
    curve: Curves.linear,
    parent: _btnAnimController,
  );

  @override
  void dispose() {
    _btnAnimController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final double buttonRadius = widget.size / 2;
    final Color resolvedSplashColor = widget.splashColor ??
        _darkenColor(widget.color, 0.6);

    return Stack(
      alignment: Alignment.center,
      children: <Widget>[
        // Animated pulse ring.
        FadeTransition(
          opacity: Tween<double>(begin: .7, end: 0).animate(_btnAnim),
          child: ScaleTransition(
            scale: Tween<double>(begin: .5, end: 1).animate(_btnAnim),
            child: CustomPaint(
              painter: CirclePainter(
                radius: buttonRadius,
                color: widget.color,
              ),
              child: SizedBox(
                width: widget.size * 1.25,
                height: widget.size * 1.25,
              ),
            ),
          ),
        ),
        // The button itself with a pulsing opacity.
        AnimatedBuilder(
          animation: _btnAnimController,
          builder: (BuildContext context, Widget? child) {
            final double opacity =
                Tween<double>(begin: .7, end: .9).transform(_btnAnim.value);
            return Container(
              width: widget.size,
              height: widget.size,
              decoration: BoxDecoration(
                color: widget.color.withValues(alpha: widget.color.a * opacity),
                shape: BoxShape.circle,
              ),
              child: Material(
                color: Colors.transparent,
                shape: const CircleBorder(),
                child: InkWell(
                  customBorder: const CircleBorder(),
                  splashColor: resolvedSplashColor,
                  hoverColor: resolvedSplashColor,
                  onTap: widget.onPressed,
                  child: Center(
                    child: Icon(
                      widget.icon,
                      size: widget.size * 0.5,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ],
    );
  }

  /// Returns a darkened version of [color] by the given [amount] (0.0 to 1.0).
  static Color _darkenColor(Color color, double amount) {
    final double factor = 1 - amount;
    final int a = (color.a * 255).round().clamp(0, 255);
    final int r = (color.r * 255 * factor).round().clamp(0, 255);
    final int g = (color.g * 255 * factor).round().clamp(0, 255);
    final int b = (color.b * 255 * factor).round().clamp(0, 255);
    return Color.fromARGB(a, r, g, b);
  }
}
