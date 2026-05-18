import 'dart:math';

import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../models/message.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';

/// 聊天消息气泡 — AI 左对齐 / 用户右对齐
class MessageBubble extends StatelessWidget {
  final Message message;

  const MessageBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == MessageRole.user;
    final cs = ShadTheme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: MellowSpacing.md,
        vertical: MellowSpacing.xs,
      ),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            _buildAvatar(isUser),
            const SizedBox(width: MellowSpacing.sm),
          ],
          Flexible(
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.75,
              ),
              child: Container(
                decoration: BoxDecoration(
                  color: isUser ? MellowColors.brandGreen : cs.muted,
                  borderRadius:
                      isUser ? MellowSpacing.bubbleUser : MellowSpacing.bubbleAi,
                  boxShadow: MellowSpacing.shadowBubble,
                ),
                padding: const EdgeInsets.all(MellowSpacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (message.isStreaming && message.content.isEmpty)
                      _TypingIndicator(
                        dotColor: isUser ? Colors.white70 : cs.mutedForeground,
                      )
                    else
                      Text(
                        message.content,
                        style: TextStyle(
                          color: isUser ? Colors.white : cs.mutedForeground,
                          fontSize: 15,
                          height: 1.5,
                        ),
                      ),
                    if (message.isFavorite)
                      Align(
                        alignment: Alignment.bottomRight,
                        child: Padding(
                          padding: const EdgeInsets.only(top: MellowSpacing.xs),
                          child: Icon(
                            Icons.star,
                            color: MellowColors.favoriteGold,
                            size: 14,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: MellowSpacing.sm),
            _buildAvatar(isUser),
          ],
        ],
      ),
    );
  }

  Widget _buildAvatar(bool isUser) {
    return CircleAvatar(
      radius: 16,
      backgroundColor:
          isUser ? MellowColors.brandGreen : MellowColors.brandOrange,
      child: isUser
          ? const Icon(Icons.person, color: Colors.white, size: 18)
          : const Text('🤖', style: TextStyle(fontSize: 16)),
    );
  }
}

/// 流式打字指示器 — 三个弹跳圆点
class _TypingIndicator extends StatefulWidget {
  final Color dotColor;

  const _TypingIndicator({required this.dotColor});

  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(3, (i) {
            final delay = i * 0.2;
            var t = (_controller.value - delay) % 1.0;
            if (t < 0) t += 1.0;
            // Easing: scale 0.5 → 1.0 → 0.5 using sine
            final scale = 0.5 + 0.5 * sin(t * pi);
            return Padding(
              padding: EdgeInsets.only(right: i < 2 ? 4.0 : 0),
              child: Transform.scale(
                scale: scale,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: widget.dotColor,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            );
          }),
        );
      },
    );
  }
}
