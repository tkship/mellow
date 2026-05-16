import 'package:flutter/foundation.dart';

import '../models/persona.dart';
import '../models/user.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiClient _client = ApiClient();
  late final AuthService _authService = AuthService(_client);

  User? _user;
  String? _token;
  bool _loading = false;

  User? get user => _user;
  bool get isLoggedIn => _token != null;
  bool get loading => _loading;
  Persona? get currentPersona => null; // 由 PersonaProvider 管理

  Future<void> tryAutoLogin() async {
    _token = await _client.loadToken();
    if (_token != null) {
      try {
        _user = await _authService.me();
      } catch (_) {
        _token = null;
      }
    }
    notifyListeners();
  }

  Future<String?> login(String username, String password) async {
    _loading = true;
    notifyListeners();
    try {
      final token = await _authService.login(username, password);
      _token = token.accessToken;
      _user = User(id: '', username: username);
      _loading = false;
      notifyListeners();
      return null;
    } catch (e) {
      _loading = false;
      notifyListeners();
      return e.toString();
    }
  }

  Future<String?> register(String username, String password) async {
    _loading = true;
    notifyListeners();
    try {
      final token = await _authService.register(username, password);
      _token = token.accessToken;
      _user = User(id: '', username: username);
      _loading = false;
      notifyListeners();
      return null;
    } catch (e) {
      _loading = false;
      notifyListeners();
      return e.toString();
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _token = null;
    _user = null;
    notifyListeners();
  }
}
