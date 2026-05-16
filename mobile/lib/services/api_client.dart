import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../config/api_config.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  final Dio _dio;
  String? _token;
  String? _refreshToken;

  ApiClient._internal() : _dio = Dio(BaseOptions(
    baseUrl: ApiConfig.baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Content-Type': 'application/json'},
  )) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_token != null) {
          options.headers['Authorization'] = 'Bearer $_token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401 &&
            _refreshToken != null &&
            error.requestOptions.path != '/api/v1/auth/refresh' &&
            error.requestOptions.extra['_retried'] != true) {
          try {
            final success = await _tryRefreshToken();
            if (success) {
              // Retry the original request with the new token
              final opts = Options(
                method: error.requestOptions.method,
                headers: Map<String, dynamic>.from(error.requestOptions.headers),
                extra: {'_retried': true},
              );
              opts.headers!['Authorization'] = 'Bearer $_token';
              final response = await _dio.request(
                error.requestOptions.path,
                data: error.requestOptions.data,
                queryParameters: error.requestOptions.queryParameters,
                options: opts,
              );
              return handler.resolve(response);
            }
          } catch (_) {
            // Refresh call itself failed
          }
          // Refresh failed — clear tokens and propagate error
          await clearToken();
        }
        handler.next(error);
      },
    ));
    // Auto-load token from SharedPreferences
    _loadTokenFromPrefs();
  }

  Future<void> _loadTokenFromPrefs() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
    _refreshToken = prefs.getString('refresh_token');
  }

  Future<void> setToken(String token, {String? refreshToken}) async {
    _token = token;
    _refreshToken = refreshToken;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
    if (refreshToken != null) {
      await prefs.setString('refresh_token', refreshToken);
    }
  }

  Future<String?> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
    return _token;
  }

  Future<void> clearToken() async {
    _token = null;
    _refreshToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
  }

  Future<bool> _tryRefreshToken() async {
    if (_refreshToken == null) return false;
    try {
      final response = await _dio.post(
        '/api/v1/auth/refresh',
        data: {'refresh_token': _refreshToken},
        options: Options(headers: {'Authorization': null}),
      );
      final data = response.data as Map<String, dynamic>;
      _token = data['access_token'] as String?;
      _refreshToken = data['refresh_token'] as String?;
      final prefs = await SharedPreferences.getInstance();
      if (_token != null) await prefs.setString('access_token', _token!);
      if (_refreshToken != null) {
        await prefs.setString('refresh_token', _refreshToken!);
      }
      debugPrint('[ApiClient] Token refreshed successfully');
      return true;
    } catch (e) {
      debugPrint('[ApiClient] Token refresh failed: $e');
      return false;
    }
  }

  bool get hasToken => _token != null;

  bool get hasRefreshToken => _refreshToken != null;

  String? get token => _token;

  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) =>
      _dio.get(path, queryParameters: queryParameters);

  Future<Response> post(String path, {dynamic data}) {
    print('[ApiClient] POST ${_dio.options.baseUrl}$path');
    return _dio.post(path, data: data);
  }

  Stream<Response> getStream(String path, {Map<String, dynamic>? queryParameters}) async* {
    final response = await _dio.get(
      path,
      queryParameters: queryParameters,
      options: Options(responseType: ResponseType.stream),
    );
    yield* response.data.stream.cast<List<int>>().transform(utf8.decoder).transform(const LineSplitter()).where((line) => line.startsWith('data: ')).map((line) => Response(
      requestOptions: response.requestOptions,
      data: line.substring(6),
    ));
  }
}


