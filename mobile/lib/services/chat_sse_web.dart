import 'dart:async';
import 'dart:convert';
import 'dart:html' as html;

/// Web 端 SSE 实现 —— 使用浏览器原生 EventSource。
Stream<String> sseStream(String url) {
  final controller = StreamController<String>();
  final source = html.EventSource(url);

  source.onMessage.listen((html.MessageEvent event) {
    try {
      final data = jsonDecode(event.data as String);
      if (data['done'] == true) {
        source.close();
        controller.close();
        return;
      }
      if (data['token'] != null) {
        controller.add(data['token'] as String);
      }
    } catch (_) {}
  });

  source.onError.listen((html.Event event) {
    source.close();
    controller.add('抱歉，连接中断了...');
    controller.close();
  });

  return controller.stream;
}
