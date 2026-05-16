import 'dart:async';

/// 非 Web 平台的 SSE 桩 —— 返回空流，实际由 Dio 处理。
Stream<String> sseStream(String url) {
  return const Stream.empty();
}
