import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../config/api_config.dart';

class ApiClient {
  final Dio _dio;
  String? _token;

  ApiClient() : _dio = Dio(BaseOptions(
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
      onError: (error, handler) => handler.next(error),
    ));
  }

  Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
  }

  Future<String?> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
    return _token;
  }

  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
  }

  bool get hasToken => _token != null;

  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) =>
      _dio.get(path, queryParameters: queryParameters);

  Future<Response> post(String path, {dynamic data}) =>
      _dio.post(path, data: data);

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

import 'dart:convert';
