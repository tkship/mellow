import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

class VoiceButton extends StatefulWidget {
  const VoiceButton({super.key, required this.onResult});

  final void Function(String text) onResult;

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton>
    with SingleTickerProviderStateMixin {
  var _recording = false;
  late final AnimationController _pulse;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(
      vsync: this,
      duration: 1000.ms,
    );
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  void _start() {
    setState(() => _recording = true);
    _pulse.repeat(reverse: true);
  }

  void _stop() {
    setState(() => _recording = false);
    _pulse.stop();
    _pulse.reset();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('语音功能开发中'),
        behavior: SnackBarBehavior.floating,
        duration: Duration(seconds: 1),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return GestureDetector(
      onLongPressStart: (_) => _start(),
      onLongPressEnd: (_) => _stop(),
      child: AnimatedContainer(
        duration: 200.ms,
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: _recording ? cs.primary : cs.surfaceContainerHighest,
          shape: BoxShape.circle,
        ),
        child: AnimatedBuilder(
          animation: _pulse,
          builder: (_, child) => Transform.scale(
            scale: _recording ? 1.0 + _pulse.value * 0.25 : 1.0,
            child: Icon(
              Icons.mic,
              size: 22,
              color: _recording ? cs.onPrimary : cs.primary,
            ),
          ),
        ),
      ),
    );
  }
}
