import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';

import 'package:mellow/features/auth/login_screen.dart';
import 'package:mellow/models/user.dart';
import 'package:mellow/providers/auth_provider.dart';
import 'package:mellow/services/api_client.dart';

class MockApiClient extends Mock implements ApiClient {}

/// Creates a minimal Dio [Response] with the given [data] payload.
Response<dynamic> _mockResponse(dynamic data) {
  return Response<dynamic>(
    requestOptions: RequestOptions(),
    data: data,
  );
}

/// Wraps [child] with a [ProviderScope] that overrides [apiClientProvider]
/// and a [MaterialApp.router] so GoRouter navigation works.
Widget _wrapApp({
  required Widget child,
  required MockApiClient mockClient,
  required GoRouter router,
}) {
  return ProviderScope(
    overrides: [apiClientProvider.overrideWithValue(mockClient)],
    child: MaterialApp.router(
      routerConfig: router,
    ),
  );
}

void main() {
  late MockApiClient mockClient;

  setUp(() {
    mockClient = MockApiClient();

    // Default stubs so AuthNotifier.build() does not crash.
    // accessToken returns null → AuthStatus.unauthenticated immediately.
    when(() => mockClient.accessToken).thenAnswer((_) async => null);
  });

  /// Builds a GoRouter that starts at /auth/login and has /personas.
  GoRouter _testRouter() {
    return GoRouter(
      initialLocation: '/auth/login',
      routes: [
        GoRoute(
          path: '/auth/login',
          builder: (_, __) => const LoginScreen(),
        ),
        GoRoute(
          path: '/auth/register',
          builder: (_, __) => const Scaffold(body: Text('register')),
        ),
        GoRoute(
          path: '/personas',
          builder: (_, __) => const Scaffold(body: Text('personas')),
        ),
      ],
    );
  }

  group('LoginScreen', () {
    // ── Rendering ──

    testWidgets('renders username and password text fields',
        (tester) async {
      await tester.pumpWidget(
        _wrapApp(
          child: const LoginScreen(),
          mockClient: mockClient,
          router: _testRouter(),
        ),
      );
      await tester.pumpAndSettle();

      // Find by label text
      expect(find.text('用户名'), findsOneWidget);
      expect(find.text('密码'), findsOneWidget);

      // Hint texts
      expect(find.text('请输入用户名'), findsOneWidget);
      expect(find.text('请输入密码'), findsOneWidget);
    });

    testWidgets('renders login button with correct label', (tester) async {
      await tester.pumpWidget(
        _wrapApp(
          child: const LoginScreen(),
          mockClient: mockClient,
          router: _testRouter(),
        ),
      );
      await tester.pumpAndSettle();

      // Login button with label '登录'
      final loginButton = find.widgetWithText(ElevatedButton, '登录');
      expect(loginButton, findsOneWidget);
    });

    // ── Validation ──

    testWidgets(
        'shows validation error when username is empty and form submitted',
        (tester) async {
      await tester.pumpWidget(
        _wrapApp(
          child: const LoginScreen(),
          mockClient: mockClient,
          router: _testRouter(),
        ),
      );
      await tester.pumpAndSettle();

      // Tap login without entering anything
      await tester.tap(find.widgetWithText(ElevatedButton, '登录'));
      await tester.pumpAndSettle();

      expect(find.text('用户名至少 3 个字符'), findsOneWidget);
    });

    testWidgets(
        'shows validation error when password is empty and form submitted',
        (tester) async {
      await tester.pumpWidget(
        _wrapApp(
          child: const LoginScreen(),
          mockClient: mockClient,
          router: _testRouter(),
        ),
      );
      await tester.pumpAndSettle();

      // Enter valid username but leave password empty
      await tester.enterText(find.byType(TextFormField).first, 'validuser');
      await tester.tap(find.widgetWithText(ElevatedButton, '登录'));
      await tester.pumpAndSettle();

      // '请输入密码' appears twice: once as hintText, once as validation error
      expect(find.text('请输入密码'), findsAtLeastNWidgets(2));
    });

    // ── Successful login ──

    testWidgets('calls login on provider when form is valid and submitted',
        (tester) async {
      // Stub successful login chain
      when(() => mockClient.login('testuser', 'password123')).thenAnswer(
        (_) async => _mockResponse({
          'access_token': 'at',
          'refresh_token': 'rt',
        }),
      );
      when(() => mockClient.getMe()).thenAnswer(
        (_) async => _mockResponse({
          'id': 'u1',
          'username': 'testuser',
          'is_active': true,
        }),
      );
      when(
        () => mockClient.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      ).thenAnswer((_) async {});

      await tester.pumpWidget(
        _wrapApp(
          child: const LoginScreen(),
          mockClient: mockClient,
          router: _testRouter(),
        ),
      );
      await tester.pumpAndSettle();

      // Fill form
      await tester.enterText(find.byType(TextFormField).first, 'testuser');
      await tester.enterText(find.byType(TextFormField).last, 'password123');
      await tester.tap(find.widgetWithText(ElevatedButton, '登录'));
      await tester.pumpAndSettle();

      // Verify API was called
      verify(() => mockClient.login('testuser', 'password123')).called(1);
    });

    testWidgets('navigates after successful login', (tester) async {
      // Stub successful login chain
      when(() => mockClient.login(any(), any())).thenAnswer(
        (_) async => _mockResponse({
          'access_token': 'at',
          'refresh_token': 'rt',
        }),
      );
      when(() => mockClient.getMe()).thenAnswer(
        (_) async => _mockResponse({
          'id': 'u1',
          'username': 'testuser',
          'is_active': true,
        }),
      );
      when(
        () => mockClient.saveTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      ).thenAnswer((_) async {});

      final router = _testRouter();
      await tester.pumpWidget(
        _wrapApp(
          child: const LoginScreen(),
          mockClient: mockClient,
          router: router,
        ),
      );
      await tester.pumpAndSettle();

      // Fill and submit
      await tester.enterText(find.byType(TextFormField).first, 'testuser');
      await tester.enterText(find.byType(TextFormField).last, 'password123');
      await tester.tap(find.widgetWithText(ElevatedButton, '登录'));
      await tester.pumpAndSettle();

      // Should navigate to /personas (check that personas page rendered)
      expect(find.text('personas'), findsOneWidget);
    });

    // ── Error display ──

    testWidgets('shows error message when login fails', (tester) async {
      // Stub login to fail
      when(() => mockClient.login(any(), any())).thenThrow(
        DioException(requestOptions: RequestOptions()),
      );

      await tester.pumpWidget(
        _wrapApp(
          child: const LoginScreen(),
          mockClient: mockClient,
          router: _testRouter(),
        ),
      );
      await tester.pumpAndSettle();

      // Fill and submit
      await tester.enterText(find.byType(TextFormField).first, 'baduser');
      await tester.enterText(find.byType(TextFormField).last, 'badpass');
      await tester.tap(find.widgetWithText(ElevatedButton, '登录'));
      await tester.pumpAndSettle();

      // Error message should appear
      expect(find.text('用户名或密码错误'), findsOneWidget);
    });
  });
}
