import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../shared/constants/error_messages.dart';

/// Mellow API 客户端 — Dio + JWT 拦截器 + SSE 流式
class ApiClient {
  static const _tokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  late final Dio dio;
  final String baseUrl;

  ApiClient({this.baseUrl = 'http://10.0.2.2:8000'}) {
    dio = Dio(BaseOptions(
      baseUrl: '$baseUrl/api/v1',
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 60),
      headers: {'Content-Type': 'application/json'},
    ));
    dio.interceptors.add(_AuthInterceptor(this));
  }

  // ── Token 管理 ──

  Future<String?> get accessToken async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<String?> get refreshToken async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_refreshTokenKey);
  }

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, accessToken);
    await prefs.setString(_refreshTokenKey, refreshToken);
  }

  Future<void> clearTokens() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_refreshTokenKey);
  }

  // ── Auth ──

  Future<Response> register(String username, String password) {
    return dio.post('/auth/register', data: {
      'username': username,
      'password': password,
    });
  }

  Future<Response> login(String username, String password) {
    return dio.post('/auth/login', data: {
      'username': username,
      'password': password,
    });
  }

  Future<Response> refreshAccessToken(String token) {
    return dio.post('/auth/refresh', data: {'refresh_token': token});
  }

  Future<Response> getMe() => dio.get('/auth/me');

  // ── Personas ──

  Future<Response> getPersonas() => dio.get('/personas');
  Future<Response> getPersonaDetail(String id) => dio.get('/personas/$id');
  Future<Response> getPersonaVoice(String id) =>
      dio.get('/personas/$id/voice', options: Options(responseType: ResponseType.bytes));

  // ── Chat ──

  Future<Response> sendMessage(String personaId, String message) {
    return dio.post('/chat', data: {
      'persona_id': personaId,
      'message': message,
    });
  }

  Future<Response> getPhrases(String personaId) {
    return dio.get('/chat/phrases', queryParameters: {'persona_id': personaId});
  }

  /// SSE 流式对话 — 返回 Stream<Map<String, dynamic>>
  Stream<Map<String, dynamic>> streamChat({
    required String personaId,
    required String message,
    String? token,
  }) async* {
    final queryParams = <String, dynamic>{
      'persona_id': personaId,
      'message': message,
    };
    if (token != null) {
      queryParams['token'] = token;
    }
    final t = token ?? await accessToken;

    try {
      final response = await dio.get<ResponseBody>(
        '/chat/stream',
        queryParameters: queryParams,
        options: Options(
          responseType: ResponseType.stream,
          headers: t != null ? {'Authorization': 'Bearer $t'} : null,
        ),
      );

      final stream = response.data?.stream;
      if (stream == null) return;

      final buffer = StringBuffer();
      await for (final chunk in stream) {
        buffer.write(utf8.decode(chunk));
        final content = buffer.toString();
        if (!content.contains('\n')) {
          // No complete line yet, wait for more data
          continue;
        }
        final lines = content.split('\n');
        // Process all lines except the last (which may be incomplete)
        for (int i = 0; i < lines.length - 1; i++) {
          final line = lines[i];
          if (line.startsWith('data: ')) {
            final jsonStr = line.substring(6).trim();
            if (jsonStr.isNotEmpty) {
              try {
                final data = jsonDecode(jsonStr) as Map<String, dynamic>;
                yield data;
              } catch (_) {
                // 忽略解析失败
              }
            }
          }
        }
        // Keep the last (possibly incomplete) line in the buffer
        buffer.clear();
        buffer.write(lines.last);
      }
    } catch (e) {
      debugPrint('SSE stream error: $e');
      rethrow;
    }
  }

  // ── Chat ──

  Future<Response> getChatHistory(
    String personaId, {
    int limit = 20,
    String? cursor,
  }) {
    final params = <String, dynamic>{
      'persona_id': personaId,
      'limit': limit,
    };
    if (cursor != null) {
      params['cursor'] = cursor;
    }
    return dio.get('/chat/history', queryParameters: params);
  }

  Future<Response> toggleMessageFavorite(String messageId, String personaId) =>
      dio.put('/chat/messages/$messageId/favorite',
          queryParameters: {'persona_id': personaId});

  Future<Response> deleteMessage(String messageId, String personaId) =>
      dio.delete('/chat/messages/$messageId',
          queryParameters: {'persona_id': personaId});

  // ── Profile ──

  Future<Response> getProfile() => dio.get('/profile');
  Future<Response> getStats({String range = 'month'}) =>
      dio.get('/profile/stats', queryParameters: {'range': range});
  Future<Response> getMistakes() => dio.get('/profile/mistakes');
  Future<Response> updateProfile(Map<String, dynamic> data) =>
      dio.put('/profile', data: data);

  // ── Vocabulary ──

  Future<Response> getVocabularyBook({String sort = 'recent'}) =>
      dio.get('/vocabulary/book', queryParameters: {'sort': sort});
  Future<Response> searchVocabulary(String query) =>
      dio.get('/vocabulary/book/search', queryParameters: {'q': query});
  Future<Response> addVocabulary(Map<String, dynamic> data) =>
      dio.post('/vocabulary/book', data: data);
  Future<Response> deleteVocabulary(String word) =>
      dio.delete('/vocabulary/book/$word');

  // ── Knowledge ──

  Future<Response> lookupWord(String word) =>
      dio.get('/knowledge/lookup', queryParameters: {'word': word});
  Future<Response> searchKnowledge(String q, {int topK = 5}) =>
      dio.get('/knowledge/search', queryParameters: {'q': q, 'top_k': topK});

  // ── Memory ──

  Future<Response> getEmotions(String personaId) =>
      dio.get('/memory/emotions', queryParameters: {'persona_id': personaId});
  Future<Response> getFacts(String personaId) =>
      dio.get('/memory/facts', queryParameters: {'persona_id': personaId});
  Future<Response> getSummary(String personaId) =>
      dio.get('/memory/summary', queryParameters: {'persona_id': personaId});
}

/// JWT 认证拦截器 — 自动附加 Token + 401 自动刷新
class _AuthInterceptor extends Interceptor {
  final ApiClient client;

  _AuthInterceptor(this.client);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await client.accessToken;
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final refresh = await client.refreshToken;
      if (refresh != null) {
        try {
          final res = await client.refreshAccessToken(refresh);
          final data = res.data as Map<String, dynamic>;
          await client.saveTokens(
            accessToken: data['access_token'] as String,
            refreshToken: data['refresh_token'] as String,
          );

          // 重试原请求
          final opts = err.requestOptions;
          opts.headers['Authorization'] =
              'Bearer ${data['access_token']}';
          final retryRes = await client.dio.fetch(opts);
          return handler.resolve(retryRes);
        } catch (_) {
          await client.clearTokens();
        }
      } else {
        await client.clearTokens();
      }
    }
    handler.next(err);
  }
}

/// 统一错误消息提取
String apiErrorMessage(DioException e) {
  if (e.type == DioExceptionType.connectionTimeout ||
      e.type == DioExceptionType.receiveTimeout) {
    return MellowErrors.networkTimeout;
  }
  if (e.type == DioExceptionType.connectionError) {
    return MellowErrors.serverUnreachable;
  }
  if (e.response?.data is Map<String, dynamic>) {
    final data = e.response!.data as Map<String, dynamic>;
    return data['message'] as String? ?? MellowErrors.requestFailed;
  }
  return MellowErrors.requestFailed;
}
