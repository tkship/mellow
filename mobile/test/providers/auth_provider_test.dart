import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:mellow/models/user.dart';
import 'package:mellow/providers/auth_provider.dart';
import 'package:mellow/services/api_client.dart';

class MockApiClient extends Mock implements ApiClient {}

Response _fakeResponse(Map<String, dynamic> data) => Response(
      requestOptions: RequestOptions(path: ''),
      data: data,
      statusCode: 200,
    );

void main() {
  late ProviderContainer container;
  late MockApiClient mockApiClient;
  late AuthNotifier notifier;

  setUp(() {
    mockApiClient = MockApiClient();
    // _checkAutoLogin() runs during build() and calls accessToken.
    // Stub it to return null so the initial build does not fail.
    when(() => mockApiClient.accessToken).thenAnswer((_) async => null);
    container = ProviderContainer(
      overrides: [
        apiClientProvider.overrideWith((ref) => mockApiClient),
      ],
    );
    notifier = container.read(authProvider.notifier);
  });

  tearDown(() {
    container.dispose();
  });

  group('initial state', () {
    test('is AuthStatus.unauthenticated after auto-login check', () {
      // _checkAutoLogin() runs during build().
      // With token stubbed to null, the state settles to unauthenticated.
      expect(notifier.state.status, AuthStatus.unauthenticated);
    });
  });

  group('login()', () {
    test('sets user state on successful API response', () async {
      when(() => mockApiClient.login('testuser', 'password123'))
          .thenAnswer((_) async => _fakeResponse({
                'access_token': 'access-123',
                'refresh_token': 'refresh-456',
              }));
      when(
        () => mockApiClient.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      ).thenAnswer((_) async {});
      when(() => mockApiClient.getMe()).thenAnswer(
        (_) async => _fakeResponse({
          'id': 'u1',
          'username': 'testuser',
          'is_active': true,
        }),
      );

      await notifier.login('testuser', 'password123');

      expect(notifier.state.status, AuthStatus.authenticated);
      expect(notifier.state.user, isNotNull);
      expect(notifier.state.user!.username, 'testuser');
      expect(notifier.state.user!.id, 'u1');
      expect(notifier.state.error, isNull);
      expect(notifier.state.isLoading, isFalse);
    });

    test('sets error state on failed API response', () async {
      when(() => mockApiClient.login('user', 'wrongpass'))
          .thenThrow(Exception('Invalid credentials'));

      await notifier.login('user', 'wrongpass');

      expect(notifier.state.status, isNot(AuthStatus.authenticated));
      expect(notifier.state.error, '用户名或密码错误');
      expect(notifier.state.user, isNull);
      expect(notifier.state.isLoading, isFalse);
    });
  });

  group('register()', () {
    test('sets user state on success', () async {
      when(() => mockApiClient.register('newuser', 'newpass'))
          .thenAnswer((_) async => _fakeResponse({
                'access_token': 'at-new',
                'refresh_token': 'rt-new',
              }));
      when(
        () => mockApiClient.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      ).thenAnswer((_) async {});
      when(() => mockApiClient.getMe()).thenAnswer(
        (_) async => _fakeResponse({
          'id': 'u2',
          'username': 'newuser',
        }),
      );

      await notifier.register('newuser', 'newpass');

      expect(notifier.state.status, AuthStatus.authenticated);
      expect(notifier.state.user, isNotNull);
      expect(notifier.state.user!.username, 'newuser');
    });
  });

  group('autoLogin()', () {
    /// Helper – creates a fresh mock + container with the given token.
    ProviderContainer _createAutoLoginContainer(
      MockApiClient mock, {
      required String? token,
    }) {
      when(() => mock.accessToken).thenAnswer((_) async => token);
      return ProviderContainer(
        overrides: [
          apiClientProvider.overrideWith((ref) => mock),
        ],
      );
    }

    test('reads token and sets user if valid', () async {
      final mock = MockApiClient();
      when(() => mock.getMe()).thenAnswer(
        (_) async => _fakeResponse({
          'id': 'u3',
          'username': 'autologin',
        }),
      );

      final c = _createAutoLoginContainer(mock, token: 'valid-token');
      final n = c.read(authProvider.notifier);

      await Future<void>.delayed(Duration.zero);

      expect(n.state.status, AuthStatus.authenticated);
      expect(n.state.user, isNotNull);
      expect(n.state.user!.username, 'autologin');

      c.dispose();
    });

    test('sets unauthenticated when token is null', () async {
      final mock = MockApiClient();
      final c = _createAutoLoginContainer(mock, token: null);
      final n = c.read(authProvider.notifier);

      await Future<void>.delayed(Duration.zero);

      expect(n.state.status, AuthStatus.unauthenticated);
      expect(n.state.user, isNull);

      c.dispose();
    });

    test('clears tokens and sets unauthenticated when getMe fails', () async {
      final mock = MockApiClient();
      when(() => mock.getMe()).thenThrow(Exception('Token expired'));
      when(() => mock.clearTokens()).thenAnswer((_) async {});

      final c = _createAutoLoginContainer(mock, token: 'stale-token');
      final n = c.read(authProvider.notifier);

      await Future<void>.delayed(Duration.zero);

      expect(n.state.status, AuthStatus.unauthenticated);
      verify(() => mock.clearTokens()).called(1);

      c.dispose();
    });
  });

  group('logout()', () {
    test('clears user state and removes token', () async {
      // Set up an authenticated state first.
      when(() => mockApiClient.login('user', 'pass')).thenAnswer(
        (_) async => _fakeResponse({
          'access_token': 'at',
          'refresh_token': 'rt',
        }),
      );
      when(
        () => mockApiClient.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      ).thenAnswer((_) async {});
      when(() => mockApiClient.getMe()).thenAnswer(
        (_) async => _fakeResponse({
          'id': 'u4',
          'username': 'user',
        }),
      );
      await notifier.login('user', 'pass');
      expect(notifier.state.status, AuthStatus.authenticated);

      // Now mock clearTokens and call logout.
      when(() => mockApiClient.clearTokens()).thenAnswer((_) async {});
      await notifier.logout();

      expect(notifier.state.status, AuthStatus.unauthenticated);
      expect(notifier.state.user, isNull);
      verify(() => mockApiClient.clearTokens()).called(1);
    });
  });
}
