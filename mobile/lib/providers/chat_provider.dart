import 'dart:async';
import 'package:flutter/foundation.dart';

import '../models/message.dart';
import '../services/api_client.dart';
import '../services/chat_service.dart';

class ChatProvider extends ChangeNotifier {
  final ApiClient _client = ApiClient();
  late final ChatService _service = ChatService(_client);

  final List<ChatMessage> _messages = [];
  bool _isStreaming = false;

  List<ChatMessage> get messages => _messages;
  bool get isStreaming => _isStreaming;

  void sendMessage(String personaId, String text) {
    final userMsg = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: text,
      role: MessageRole.user,
    );
    _messages.add(userMsg);
    notifyListeners();

    _startStreaming(personaId, text);
  }

  void _startStreaming(String personaId, String text) {
    _isStreaming = true;
    final botMsg = ChatMessage(
      id: 'stream_${DateTime.now().millisecondsSinceEpoch}',
      content: '',
      role: MessageRole.assistant,
      isStreaming: true,
    );
    _messages.add(botMsg);
    notifyListeners();

    _service.streamMessage(personaId, text).listen(
      (token) {
        botMsg.content += token;
        notifyListeners();
      },
      onDone: () {
        botMsg.isStreaming = false;
        _isStreaming = false;
        notifyListeners();
      },
      onError: (_) {
        botMsg.content = '消息发送失败，请重试。';
        botMsg.isStreaming = false;
        _isStreaming = false;
        notifyListeners();
      },
    );
  }
}
