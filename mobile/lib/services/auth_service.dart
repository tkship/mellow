import 'api_client.dart';
import '../models/user.dart';

class AuthService {
  final ApiClient _client;

  AuthService(this._client);

  Future<Token> register(String username, String password) async {
    final res = await _client.post('/api/v1/auth/register', data: {
      'username': username,
      'password': password,
    });
    final token = Token.fromJson(res.data);
    await _client.setToken(token.accessToken);
    return token;
  }

  Future<Token> login(String username, String password) async {
    final res = await _client.post('/api/v1/auth/login', data: {
      'username': username,
      'password': password,
    });
    final token = Token.fromJson(res.data);
    await _client.setToken(token.accessToken);
    return token;
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
