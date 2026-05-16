import 'package:flutter/material.dart';

class VoiceButton extends StatefulWidget {
  const VoiceButton({super.key, required this.onResult});
  final void Function(String text) onResult;
  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton> with SingleTickerProviderStateMixin {
  var _on = false;
  late final _p = AnimationController(vsync: this, duration: const Duration(milliseconds: 1000));
  @override
  void dispose() { _p.dispose(); super.dispose(); }

  void _down() { setState(() => _on = true); _p.repeat(reverse: true); }
  void _up() {
    setState(() => _on = false); _p.stop(); _p.reset();
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('语音功能开发中'), behavior: SnackBarBehavior.floating));
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return GestureDetector(
      onLongPressStart: (_) => _down(), onLongPressEnd: (_) => _up(),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200), width: 44, height: 44,
        decoration: BoxDecoration(color: _on ? cs.primary : cs.surfaceContainerHighest, shape: BoxShape.circle),
        child: AnimatedBuilder(
          animation: _p,
          builder: (_, c) => Transform.scale(scale: _on ? 1 + _p.value * 0.22 : 1,
            child: Icon(Icons.mic, size: 20, color: _on ? cs.onPrimary : cs.primary)),
        ),
      ),
    );
  }
}
