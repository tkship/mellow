import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/chat_provider.dart';
import '../providers/persona_provider.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/typing_indicator.dart';
import '../widgets/voice_button.dart';
import '../models/message.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _textCtrl = TextEditingController();
  final _scrollCtrl = ScrollController();

  void _sendMessage() {
    final text = _textCtrl.text.trim();
    if (text.isEmpty) return;

    final persona = context.read<PersonaProvider>().selected;
    if (persona == null) return;

    context.read<ChatProvider>().sendMessage(persona.id, text);
    _textCtrl.clear();
  }

  void _onVoiceResult(String text) {
    if (text.isNotEmpty) {
      _textCtrl.text = text;
      _sendMessage();
    }
  }

  @override
  void dispose() {
    _textCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chat = context.watch<ChatProvider>();
    final persona = context.watch<PersonaProvider>().selected;
    final theme = Theme.of(context);

    // 自动滚动到底部
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(_scrollCtrl.position.maxScrollExtent,
            duration: const Duration(milliseconds: 200), curve: Curves.easeOut);
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Text(persona?.roleEmoji ?? '🌟', style: const TextStyle(fontSize: 24)),
            const SizedBox(width: 8),
            Text(persona?.name ?? 'Mellow'),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.book), onPressed: () {}), // 学习计划
          IconButton(icon: const Icon(Icons.search), onPressed: () {}), // 查词
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: chat.messages.isEmpty
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.chat_bubble_outline, size: 64, color: theme.colorScheme.primary.withAlpha(100)),
                        const SizedBox(height: 16),
                        Text('和 ${persona?.name ?? 'Mellow'} 开始对话吧',
                            style: theme.textTheme.bodyLarge?.copyWith(color: Colors.grey)),
                      ],
                    ),
                  )
                : ListView.builder(
                    controller: _scrollCtrl,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    itemCount: chat.messages.length,
                    itemBuilder: (_, i) => ChatBubble(message: chat.messages[i]),
                  ),
          ),
          if (chat.isStreaming) const TypingIndicator(),
          _buildInputBar(theme),
        ],
      ),
    );
  }

  Widget _buildInputBar(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 4, offset: const Offset(0, -1))],
      ),
      child: Row(
        children: [
          VoiceButton(onResult: _onVoiceResult),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              controller: _textCtrl,
              decoration: InputDecoration(
                hintText: '输入消息...',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(24)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              ),
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          const SizedBox(width: 8),
          IconButton.filled(
            onPressed: _sendMessage,
            icon: const Icon(Icons.send),
          ),
        ],
      ),
    );
  }
}
