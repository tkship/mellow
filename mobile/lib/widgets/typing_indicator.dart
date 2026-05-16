import 'package:flutter/material.dart';

class TypingIndicator extends StatefulWidget {
  const TypingIndicator({super.key});

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(left: 20, bottom: 12),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          decoration: BoxDecoration(
            color: cs.surfaceContainerHighest.withAlpha(150),
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(22),
              topRight: Radius.circular(22),
              bottomRight: Radius.circular(22),
              bottomLeft: Radius.circular(6),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              for (var i = 0; i < 3; i++) ...[
                if (i > 0) const SizedBox(width: 5),
                BouncingDot(ctrl: _ctrl, index: i, color: cs.primary),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class BouncingDot extends StatelessWidget {
  const BouncingDot({
    super.key,
    required this.ctrl,
    required this.index,
    required this.color,
  });

  final AnimationController ctrl;
  final int index;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: ctrl,
      builder: (_, __) {
        final v = (ctrl.value - index * 0.22) % 1.0;
        final scale = v < 0.5 ? 0.4 + v * 1.2 : 1.0 - (v - 0.5) * 1.2;
        final opacity = v < 0.5 ? 0.3 + v * 1.4 : 1.0 - (v - 0.5) * 1.4;
        return Opacity(
          opacity: opacity.clamp(0.3, 1.0),
          child: Transform.scale(
            scale: scale.clamp(0.4, 1.0),
            child: Container(
              width: 7,
              height: 7,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
            ),
          ),
        );
      },
    );
  }
}
