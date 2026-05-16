import 'package:flutter/material.dart';

/// 语音按钮 —— 按住说话，松开发送。
/// Phase 7 提供 UI 骨架，Phase 8 接入实际录音功能。
class VoiceButton extends StatefulWidget {
  final void Function(String text) onResult;

  const VoiceButton({super.key, required this.onResult});

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton> {
  bool _isRecording = false;

  void _startRecording() => setState(() => _isRecording = true);
  void _stopRecording() {
    setState(() => _isRecording = false);
    // TODO Phase 8: 实际 ASR 调用
    // widget.onResult(recognizedText);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onLongPressStart: (_) => _startRecording(),
      onLongPressEnd: (_) => _stopRecording(),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: _isRecording ? Colors.red : theme.colorScheme.primaryContainer,
          shape: BoxShape.circle,
        ),
        child: Icon(
          _isRecording ? Icons.mic : Icons.mic_none,
          color: _isRecording ? Colors.white : theme.colorScheme.primary,
        ),
      ),
    );
  }
}
