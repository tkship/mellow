import 'dart:async';
import 'dart:convert';

import 'api_client.dart';

class ChatService {
  final ApiClient _client;

  ChatService(this._client);

  Future<Map<String, dynamic>> sendMessage(String personaId, String message) async {
    final res = await _client.post('/api/v1/chat', data: {
      'persona_id': personaId,
      'message': message,
    });
    return res.data;
  }

  Stream<String> streamMessage(String personaId, String message) async* {
    final uri = '/api/v1/chat/stream?persona_id=$personaId&message=${Uri.encodeComponent(message)}';
    try {
      await for (final chunk in _client.getStream(uri)) {
        try {
          final data = jsonDecode(chunk.data);
          if (data['done'] == true) break;
          if (data['token'] != null) yield data['token'];
        } catch (_) {}
      }
    } catch (_) {
      yield '抱歉，连接中断了...';
    }
  }
}
