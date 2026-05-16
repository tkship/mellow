import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

import '../models/message.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  final String? personaEmoji;
  final String? personaName;

  const ChatBubble({
    super.key,
    required this.message,
    this.personaEmoji,
    this.personaName,
  });

  String _formatTime(DateTime dt) {
    final h = dt.hour.toString().padLeft(2, '0');
    final m = dt.minute.toString().padLeft(2, '0');
    return '$h:$m';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isUser = message.isUser;

    final avatar = CircleAvatar(
      radius: 16,
      backgroundColor: isUser
          ? theme.colorScheme.primary
          : theme.colorScheme.secondaryContainer,
      child: Text(
        isUser ? '👤' : (personaEmoji ?? '🤖'),
        style: const TextStyle(fontSize: 14),
      ),
    );

    final bubble = Container(
      constraints: BoxConstraints(
        maxWidth: MediaQuery.of(context).size.width * 0.75,
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isUser
              ? [
                  theme.colorScheme.primaryContainer,
                  theme.colorScheme.primaryContainer,
                  theme.colorScheme.secondaryContainer.withOpacity(0.3),
                ]
              : [
                  theme.colorScheme.surfaceContainerHighest,
                  theme.colorScheme.surfaceContainerHighest,
                  theme.colorScheme.primaryContainer.withOpacity(0.15),
                ],
        ),
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(20),
          topRight: const Radius.circular(20),
          bottomLeft:
              isUser ? const Radius.circular(20) : const Radius.circular(4),
          bottomRight:
              isUser ? const Radius.circular(4) : const Radius.circular(20),
        ),
        border: isUser
            ? null
            : Border(
                left: BorderSide(
                  color: theme.colorScheme.primary.withOpacity(0.25),
                  width: 3,
                ),
              ),
        boxShadow: [
          BoxShadow(
            color: isUser
                ? theme.colorScheme.primary.withOpacity(0.08)
                : theme.colorScheme.shadow.withOpacity(0.04),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment:
            isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // Name label for bot messages
          if (!isUser && personaName != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 6,
                    height: 6,
                    margin: const EdgeInsets.only(right: 6),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: theme.colorScheme.primary.withOpacity(0.4),
                          blurRadius: 4,
                        ),
                      ],
                    ),
                  ),
                  Text(
                    personaName!,
                    style: theme.textTheme.labelLarge?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          // Message content or streaming dots
          if (message.isStreaming && message.content.isEmpty)
            const _StreamingDots()
          else if (isUser)
            Text(
              message.content,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onPrimaryContainer,
              ),
            )
          else
            MarkdownBody(
              data: message.content,
              selectable: true,
              styleSheet: MarkdownStyleSheet(
                p: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurface,
                ),
                code: theme.textTheme.bodySmall?.copyWith(
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                ),
                codeblockDecoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          const SizedBox(height: 6),
          // Timestamp
          Text(
            _formatTime(message.timestamp),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.outline.withOpacity(0.6),
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: isUser
            ? [
                Flexible(child: bubble),
                const SizedBox(width: 8),
                avatar,
              ]
            : [
                avatar,
                const SizedBox(width: 8),
                Flexible(child: bubble),
              ],
      ),
    ).animate().fadeIn(duration: 300.ms).slideX(begin: isUser ? 20 : -20);
  }
}

// -- Private streaming dots (3 pulsing dots) --

class _StreamingDots extends StatelessWidget {
  const _StreamingDots();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: const [
        _PulseDot(delayMs: 0),
        SizedBox(width: 4),
        _PulseDot(delayMs: 200),
        SizedBox(width: 4),
        _PulseDot(delayMs: 400),
      ],
    );
  }
}

class _PulseDot extends StatefulWidget {
  final int delayMs;
  const _PulseDot({required this.delayMs});

  @override
  State<_PulseDot> createState() => _PulseDotState();
}

class _PulseDotState extends State<_PulseDot>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    Future.delayed(Duration(milliseconds: widget.delayMs), () {
      if (mounted) _ctrl.repeat(reverse: true);
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, child) =>
          Opacity(opacity: 0.3 + _ctrl.value * 0.7, child: child),
      child: Container(
        width: 6,
        height: 6,
        decoration: BoxDecoration(
          color: theme.colorScheme.primary.withOpacity(0.5),
          shape: BoxShape.circle,
        ),
      ),
    );
  }
}
