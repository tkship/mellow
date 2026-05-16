import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../models/message.dart';

class ChatBubble extends StatelessWidget {
  const ChatBubble({super.key, required this.message, this.emoji, this.name});
  final ChatMessage message;
  final String? emoji;
  final String? name;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final isMine = message.isUser;
    final w = MediaQuery.of(context).size.width;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 3),
      child: Column(
        crossAxisAlignment: isMine ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          if (!isMine && name != null)
            Padding(
              padding: const EdgeInsets.only(left: 16, bottom: 3),
              child: Row(mainAxisSize: MainAxisSize.min, children: [
                if (emoji != null) Text(emoji!, style: const TextStyle(fontSize: 13)),
                if (emoji != null) const SizedBox(width: 4),
                Text(name!, style: theme.textTheme.labelSmall?.copyWith(color: cs.outline, fontWeight: FontWeight.w600)),
              ]),
            ),
          Container(
            constraints: BoxConstraints(maxWidth: w * 0.72),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: isMine ? cs.primary : cs.surfaceContainerHighest,
              borderRadius: BorderRadius.only(
                topLeft: const Radius.circular(20), topRight: const Radius.circular(20),
                bottomLeft: Radius.circular(isMine ? 20 : 5), bottomRight: Radius.circular(isMine ? 5 : 20),
              ),
            ),
            child: isMine
                ? Text(message.content, style: theme.textTheme.bodyMedium?.copyWith(color: cs.onPrimary, height: 1.45))
                : Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
                    MarkdownBody(
                      data: message.content, selectable: true,
                      styleSheet: MarkdownStyleSheet(
                        p: theme.textTheme.bodyMedium?.copyWith(height: 1.45),
                        code: theme.textTheme.bodySmall?.copyWith(backgroundColor: cs.surface, fontFamily: 'monospace'),
                        codeblockDecoration: BoxDecoration(color: cs.surface, borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                    if (message.isStreaming) const _Cursor(),
                  ]),
          ),
          const SizedBox(height: 2),
          Padding(
            padding: EdgeInsets.only(left: isMine ? 0 : 16, right: isMine ? 16 : 0),
            child: Text(
              '${message.timestamp.hour.toString().padLeft(2, '0')}:${message.timestamp.minute.toString().padLeft(2, '0')}',
              style: theme.textTheme.labelSmall?.copyWith(color: cs.outlineVariant),
            ),
          ),
        ],
      ),
    );
  }
}

class _Cursor extends StatefulWidget {
  const _Cursor();
  @override
  State<_Cursor> createState() => _CursorState();
}

class _CursorState extends State<_Cursor> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 600))..repeat(reverse: true);
  @override
  void dispose() { _c.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _c,
      child: Text('|', style: TextStyle(color: Theme.of(context).colorScheme.primary, fontWeight: FontWeight.w300, fontSize: 18)),
    );
  }
}
