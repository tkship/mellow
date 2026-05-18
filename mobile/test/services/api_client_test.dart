import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:mellow/services/api_client.dart';

class MockHttpClientAdapter extends Mock implements HttpClientAdapter {}

void main() {
  setUpAll(() {
    registerFallbackValue(RequestOptions(path: ''));
    registerFallbackValue(Stream<List<int>>.empty());
  });

  group('apiErrorMessage', () {
    test('returns timeout message for connectionTimeout', () {
      final error = DioException(
        type: DioExceptionType.connectionTimeout,
        requestOptions: RequestOptions(path: ''),
      );
      expect(apiErrorMessage(error), contains('超时'));
    });

    test('returns timeout message for receiveTimeout', () {
      final error = DioException(
        type: DioExceptionType.receiveTimeout,
        requestOptions: RequestOptions(path: ''),
      );
      expect(apiErrorMessage(error), contains('超时'));
    });

    test('returns connection error for connectionError', () {
      final error = DioException(
        type: DioExceptionType.connectionError,
        requestOptions: RequestOptions(path: ''),
      );
      expect(apiErrorMessage(error), contains('无法连接'));
    });

    test('extracts message from response data', () {
      final error = DioException(
        type: DioExceptionType.badResponse,
        requestOptions: RequestOptions(path: ''),
        response: Response(
          requestOptions: RequestOptions(path: ''),
          data: {'message': '自定义错误信息'},
        ),
      );
      expect(apiErrorMessage(error), '自定义错误信息');
    });

    test('returns default when message is null in response', () {
      final error = DioException(
        type: DioExceptionType.badResponse,
        requestOptions: RequestOptions(path: ''),
        response: Response(
          requestOptions: RequestOptions(path: ''),
          data: {'other': 'value'},
        ),
      );
      expect(apiErrorMessage(error), '请求失败，请稍后重试');
    });

    test('returns default for non-map response data', () {
      final error = DioException(
        type: DioExceptionType.badResponse,
        requestOptions: RequestOptions(path: ''),
        response: Response(
          requestOptions: RequestOptions(path: ''),
          data: 'plain text',
        ),
      );
      expect(apiErrorMessage(error), '请求失败，请稍后重试');
    });
  });

  group('JWT Interceptor', () {
    late ApiClient apiClient;
    late MockHttpClientAdapter mockAdapter;

    setUp(() {
      mockAdapter = MockHttpClientAdapter();
    });

    test('attaches Bearer token on request when token exists', () async {
      SharedPreferences.setMockInitialValues({'access_token': 'test-jwt-token'});
      apiClient = ApiClient();
      apiClient.dio.httpClientAdapter = mockAdapter;

      RequestOptions? capturedOptions;
      when(() => mockAdapter.fetch(any(), any(), any()))
          .thenAnswer((inv) async {
        capturedOptions = inv.positionalArguments[0] as RequestOptions;
        return ResponseBody.fromString('{"ok": true}', 200);
      });

      await apiClient.getMe();

      expect(capturedOptions, isNotNull);
      expect(
        capturedOptions!.headers['Authorization'],
        'Bearer test-jwt-token',
      );
    });

    test('does NOT attach token when token is null', () async {
      SharedPreferences.setMockInitialValues({});
      apiClient = ApiClient();
      apiClient.dio.httpClientAdapter = mockAdapter;

      RequestOptions? capturedOptions;
      when(() => mockAdapter.fetch(any(), any(), any()))
          .thenAnswer((inv) async {
        capturedOptions = inv.positionalArguments[0] as RequestOptions;
        return ResponseBody.fromString('{"ok": true}', 200);
      });

      await apiClient.getMe();

      expect(capturedOptions, isNotNull);
      expect(
        capturedOptions!.headers.containsKey('Authorization'),
        isFalse,
      );
    });

    test('401 response triggers token refresh and retry', () async {
      SharedPreferences.setMockInitialValues({
        'access_token': 'old_token',
        'refresh_token': 'old_refresh',
      });
      apiClient = ApiClient();
      apiClient.dio.httpClientAdapter = mockAdapter;

      /// Helper that creates a ResponseBody whose stream is guaranteed
      /// to deliver data synchronously when listened to.
      ResponseBody _makeResponseBody(String json, int statusCode) {
        final ctrl = StreamController<Uint8List>(sync: true);
        ctrl.add(utf8.encode(json) as Uint8List);
        ctrl.close();
        return ResponseBody(
          ctrl.stream,
          statusCode,
          headers: {'content-type': ['application/json']},
        );
      }

      // Mock the adapter to handle refresh + retry calls.
      int callCount = 0;
      when(() => mockAdapter.fetch(any(), any(), any()))
          .thenAnswer((inv) async {
        callCount++;
        if (callCount == 1) {
          // Refresh request
          return _makeResponseBody(
            '{"access_token": "new_token", "refresh_token": "new_refresh"}',
            200,
          );
        } else {
          // Retry of original request
          return _makeResponseBody(
            '{"id": "1", "username": "test"}',
            200,
          );
        }
      });

      // Access the _AuthInterceptor directly.
      // It is the second interceptor (index 1; index 0 is Dio's
      // built-in ImplyContentTypeInterceptor).
      final authInterceptor = apiClient.dio.interceptors[1];

      // Simulate a 401 error using the canonical Dio factory.
      final reqOpts = RequestOptions(path: '/auth/me');
      final errResp = Response(
        requestOptions: reqOpts,
        statusCode: 401,
        data: {'detail': 'unauthorized'},
      );
      final dioErr = DioException.badResponse(
        statusCode: 401,
        requestOptions: reqOpts,
        response: errResp,
      );

      final handler = ErrorInterceptorHandler();
      authInterceptor.onError(dioErr, handler);

      // Wait for the handler to settle (resolve or next/reject).
      bool resolved = false;
      try {
        await handler.future;
        resolved = true;
      } catch (_) {
        // handler.next() or handler.reject() was called.
      }

      final prefs = await SharedPreferences.getInstance();

      expect(resolved, isTrue,
          reason: 'Expected handler.resolve() to be called, '
              'but handler.next()/reject() was called instead. '
              'callCount=$callCount, '
              'access_token=${prefs.getString("access_token") ?? "null"}, '
              'refresh_token=${prefs.getString("refresh_token") ?? "null"}');

      // Full success — refresh + retry both completed.
      expect(callCount, 2);
      expect(prefs.getString('access_token'), 'new_token');
      expect(prefs.getString('refresh_token'), 'new_refresh');
    });
  });

  group('SSE stream parsing', () {
    late ApiClient apiClient;
    late MockHttpClientAdapter mockAdapter;

    setUp(() {
      SharedPreferences.setMockInitialValues({});
      mockAdapter = MockHttpClientAdapter();
    });

    test('handles valid data: frames and yields parsed maps', () async {
      apiClient = ApiClient();
      apiClient.dio.httpClientAdapter = mockAdapter;

      final sseChunks = [
        utf8.encode('data: {"token": "Hello"}\n'),
        utf8.encode('data: {"token": " World"}\n'),
        utf8.encode('data: {"done": true}\n'),
      ];

      final responseBody = ResponseBody(
        Stream.fromIterable(sseChunks),
        200,
        headers: {'content-type': ['text/event-stream']},
      );

      when(() => mockAdapter.fetch(any(), any(), any()))
          .thenAnswer((_) async => responseBody);

      final results = <Map<String, dynamic>>[];
      final stream = apiClient.streamChat(
        personaId: 'p1',
        message: 'hi',
      );

      await for (final data in stream) {
        results.add(data);
      }

      expect(results.length, 3);
      expect(results[0], {'token': 'Hello'});
      expect(results[1], {'token': ' World'});
      expect(results[2], {'done': true});
    });

    test('ignores lines without data: prefix', () async {
      apiClient = ApiClient();
      apiClient.dio.httpClientAdapter = mockAdapter;

      final sseChunks = [
        utf8.encode(':comment line\n'),
        utf8.encode('data: {"token": "valid"}\n'),
        utf8.encode('\n'),
      ];

      final responseBody = ResponseBody(
        Stream.fromIterable(sseChunks),
        200,
        headers: {'content-type': ['text/event-stream']},
      );

      when(() => mockAdapter.fetch(any(), any(), any()))
          .thenAnswer((_) async => responseBody);

      final results = <Map<String, dynamic>>[];
      final stream = apiClient.streamChat(
        personaId: 'p1',
        message: 'hi',
      );

      await for (final data in stream) {
        results.add(data);
      }

      expect(results.length, 1);
      expect(results.first, {'token': 'valid'});
    });
  });
}
