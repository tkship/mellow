import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../models/persona.dart';
import '../models/user.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiClient _client = ApiClient();
  late final AuthService _authService = AuthService(_client);

  User? _user;
  Token? _token;
  bool _loading = false;

  User? get user => _user;
  bool get isLoggedIn => _token != null;
  bool get loading => _loading;
  Persona? get currentPersona => null; // 由 PersonaProvider 管理

  Future<void> tryAutoLogin() async {
    final accessToken = await _client.loadToken();
    if (accessToken != null) {
      _token = Token(accessToken: accessToken, refreshToken: '', expiresIn: 0);
      try {
        _user = await _authService.me();
      } catch (_) {
        _token = null;
      }
    }
    notifyListeners();
  }

  Future<String?> login(String username, String password) async {
    debugPrint('[AuthProvider] login() called with username="$username"');
    _loading = true;
    notifyListeners();
    try {
      final token = await _authService.login(username, password);
      final tokLen = token.accessToken.length;
      debugPrint('[AuthProvider] login() succeeded, token=${token.accessToken.substring(0, tokLen < 10 ? tokLen : 10)}...');
      _token = token;
      _user = User(id: '', username: username);
      _loading = false;
      notifyListeners();
      return null;
    } catch (e) {
      debugPrint('[AuthProvider] login() failed: $e');
      _loading = false;
      notifyListeners();
      if (e is DioException && e.response?.data != null) {
        final data = e.response!.data;
        if (data is Map) {
          final detail = data['detail'];
          final message = data['message'];
          // 后端 detail 永远是 {}（空 Map），真正的错误信息在 message
          if (detail is String && detail.isNotEmpty) {
            return detail;
          }
          if (message is String && message.isNotEmpty) {
            return message;
          }
          if (detail is List && detail.isNotEmpty) {
            return detail.map((d) => d is Map ? d['msg'] ?? d.toString() : d.toString()).join('；');
          }
        }
      }
      return '登录失败，请稍后重试';
    }
  }

  Future<String?> register(String username, String password) async {
    debugPrint('[AuthProvider] register() called with username="$username"');
    _loading = true;
    notifyListeners();
    try {
      final token = await _authService.register(username, password);
      final tokLen = token.accessToken.length;
      debugPrint('[AuthProvider] register() succeeded, token=${token.accessToken.substring(0, tokLen < 10 ? tokLen : 10)}...');
      _token = token;
      _user = User(id: '', username: username);
      _loading = false;
      notifyListeners();
      return null;
    } catch (e) {
      debugPrint('[AuthProvider] register() failed: $e');
      _loading = false;
      notifyListeners();
      if (e is DioException && e.response?.data != null) {
        final data = e.response!.data;
        if (data is Map) {
          final detail = data['detail'];
          final message = data['message'];
          // 后端 detail 永远是 {}（空 Map），真正的错误信息在 message
          if (detail is String && detail.isNotEmpty) {
            return detail;
          }
          if (message is String && message.isNotEmpty) {
            return message;
          }
          if (detail is List && detail.isNotEmpty) {
            return detail.map((d) => d is Map ? d['msg'] ?? d.toString() : d.toString()).join('；');
          }
        }
      }
      return '注册失败，请稍后重试';
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _token = null;
    _user = null;
    notifyListeners();
  }
}
