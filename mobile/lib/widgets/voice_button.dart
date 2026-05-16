import 'package:flutter/material.dart';

/// 语音按钮 —— 按住说话，松开发送。
/// Phase 7 提供 UI 骨架，Phase 8 接入实际录音功能。
class VoiceButton extends StatefulWidget {
  final void Function(String text) onResult;

  const VoiceButton({super.key, required this.onResult});

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton>
    with SingleTickerProviderStateMixin {
  bool _isRecording = false;
  late final AnimationController _pulseCtrl;
  late final Animation<double> _pulseScale;
  late final Animation<double> _pulseOpacity;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _pulseScale = Tween<double>(begin: 0.8, end: 1.3).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeOut),
    );
    _pulseOpacity = Tween<double>(begin: 0.4, end: 0.0).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeOut),
    );
    _pulseCtrl.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _pulseCtrl.repeat();
      }
    });
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    super.dispose();
  }

  void _startRecording() {
    setState(() => _isRecording = true);
    _pulseCtrl.forward(from: 0.0);
  }

  void _stopRecording() {
    setState(() => _isRecording = false);
    _pulseCtrl.reset();
    // TODO Phase 8: 接入 ASR 后调用 widget.onResult(recognizedText);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('语音识别功能开发中，敬请期待 🎙️'),
        duration: Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return GestureDetector(
      onLongPressStart: (_) => _startRecording(),
      onLongPressEnd: (_) => _stopRecording(),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Pulse ring — visible only when recording
          if (_isRecording)
            AnimatedBuilder(
              animation: _pulseCtrl,
              builder: (_, child) => Transform.scale(
                scale: _pulseScale.value,
                child: Opacity(
                  opacity: _pulseOpacity.value,
                  child: Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: cs.error,
                        width: 3,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          // Actual button
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: _isRecording ? cs.error : cs.primaryContainer,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: (_isRecording ? cs.error : cs.primary)
                      .withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Icon(
              _isRecording ? Icons.mic_rounded : Icons.mic_none_rounded,
              color: _isRecording ? cs.onError : cs.primary,
              size: 22,
            ),
          ),
        ],
      ),
    );
  }
}
