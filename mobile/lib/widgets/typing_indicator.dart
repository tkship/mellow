import 'package:flutter/material.dart';

class TypingIndicator extends StatefulWidget {
  const TypingIndicator({super.key});
  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1400))..repeat();
  @override
  void dispose() { _c.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(left: 18, bottom: 10),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: cs.surfaceContainerHighest,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(20), topRight: Radius.circular(20),
              bottomRight: Radius.circular(20), bottomLeft: Radius.circular(6),
            ),
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            for (var i = 0; i < 3; i++) ...[
              if (i > 0) const SizedBox(width: 5),
              _Dot(ctrl: _c, idx: i, color: cs.primary),
            ],
          ]),
        ),
      ),
    );
  }
}

class _Dot extends StatelessWidget {
  const _Dot({required this.ctrl, required this.idx, required this.color});
  final AnimationController ctrl;
  final int idx;
  final Color color;
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: ctrl,
      builder: (_, __) {
        final v = (ctrl.value - idx * 0.22) % 1.0;
        final s = v < 0.5 ? 0.4 + v * 1.2 : 1.0 - (v - 0.5) * 1.2;
        return Opacity(
          opacity: (v < 0.5 ? 0.3 + v * 1.4 : 1.0 - (v - 0.5) * 1.4).clamp(0.3, 1.0),
          child: Transform.scale(scale: s.clamp(0.4, 1.0),
            child: Container(width: 7, height: 7, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          ),
        );
      },
    );
  }
}
