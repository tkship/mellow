import 'api_client.dart';
import '../models/user.dart';

class AuthService {
  final ApiClient _client;

  AuthService(this._client);

  Future<Token> register(String username, String password) async {
    print('[AuthService] register() → POST /api/v1/auth/register');
    final res = await _client.post('/api/v1/auth/register', data: {
      'username': username,
      'password': password,
    });
    print('[AuthService] register() response: ${res.statusCode}');
    final token = Token.fromJson(res.data);
    await _client.setToken(token.accessToken, refreshToken: token.refreshToken);
    return token;
  }

  Future<Token> login(String username, String password) async {
    print('[AuthService] login() → POST /api/v1/auth/login');
    final res = await _client.post('/api/v1/auth/login', data: {
      'username': username,
      'password': password,
    });
    print('[AuthService] login() response: ${res.statusCode}');
    final token = Token.fromJson(res.data);
    await _client.setToken(token.accessToken, refreshToken: token.refreshToken);
    return token;
  }

  Future<Token> refreshToken(String refreshToken) async {
    print('[AuthService] refreshToken() → POST /api/v1/auth/refresh');
    final res = await _client.post('/api/v1/auth/refresh', data: {
      'refresh_token': refreshToken,
    });
    print('[AuthService] refreshToken() response: ${res.statusCode}');
    return Token.fromJson(res.data);
  }

  Future<void> logout() => _client.clearToken();

  Future<User?> me() async {
    try {
      final res = await _client.get('/api/v1/auth/me');
      return User.fromJson(res.data);
    } catch (_) {
      return null;
    }
  }
}
