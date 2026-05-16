import 'dart:async';
import 'dart:convert';

import 'api_client.dart';
import '../config/api_config.dart';
import 'chat_sse_stub.dart' if (dart.library.html) 'chat_sse_web.dart';

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
    final token = _client.token ?? '';
    final encodedMsg = Uri.encodeComponent(message);
    final url =
        '${ApiConfig.baseUrl}${ApiConfig.apiPrefix}/chat/stream'
        '?persona_id=$personaId'
        '&message=$encodedMsg'
        '&token=$token';

    // Web 平台走浏览器原生 EventSource（SSE）
    final webStream = sseStream(url);
    final c = StreamController<String>();
    bool emitted = false;

    webStream.listen(
      (data) {
        emitted = true;
        c.add(data);
      },
      onDone: () {
        if (!emitted) {
          // 非 Web 平台返回空流 → 降级到 Dio
          _dioStream(personaId, encodedMsg, token).listen(
            c.add,
            onError: (_) => c.add('抱歉，连接中断了...'),
            onDone: c.close,
          );
        } else {
          c.close();
        }
      },
      onError: (_) {
        c.add('抱歉，连接中断了...');
        c.close();
      },
    );

    yield* c.stream;
  }

  Stream<String> _dioStream(String personaId, String encodedMsg, String token) async* {
    final uri =
        '/api/v1/chat/stream'
        '?persona_id=$personaId'
        '&message=$encodedMsg'
        '&token=$token';
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
