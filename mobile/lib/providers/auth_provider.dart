import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/user.dart';
import '../services/api_client.dart';
import '../shared/constants/error_messages.dart';

/// 认证状态
enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? error;
  final bool isLoading;

  const AuthState({
    this.status = AuthStatus.unknown,
    this.user,
    this.error,
    this.isLoading = false,
  });

  AuthState copyWith({
    AuthStatus? status,
    User? user,
    String? error,
    bool? isLoading,
    bool clearError = false,
  }) =>
      AuthState(
        status: status ?? this.status,
        user: user ?? this.user,
        error: clearError ? null : (error ?? this.error),
        isLoading: isLoading ?? this.isLoading,
      );
}

/// API 客户端单例
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

/// 认证状态 Notifier
class AuthNotifier extends Notifier<AuthState> {
  @override
  AuthState build() {
    // 启动时检查自动登录
    _checkAutoLogin();
    return const AuthState();
  }

  Future<void> _checkAutoLogin() async {
    final client = ref.read(apiClientProvider);
    final token = await client.accessToken;
    if (token == null) {
      state = state.copyWith(status: AuthStatus.unauthenticated);
      return;
    }
    try {
      final res = await client.getMe();
      final user = User.fromJson(res.data as Map<String, dynamic>);
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } catch (e) {
      debugPrint('Auto-login check failed: $e');
      // Token 失效，清除
      await client.clearTokens();
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> login(String username, String password) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.login(username, password);
      final data = res.data as Map<String, dynamic>;
      await client.saveTokens(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
      );

      // 获取用户信息
      final me = await client.getMe();
      final user = User.fromJson(me.data as Map<String, dynamic>);
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } catch (e) {
      final msg =
          e is DioException ? apiErrorMessage(e) : MellowErrors.wrongCredentials;
      state = state.copyWith(isLoading: false, error: msg);
    }
  }

  Future<void> register(String username, String password) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.register(username, password);
      final data = res.data as Map<String, dynamic>;
      await client.saveTokens(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
      );

      // 获取用户信息
      final me = await client.getMe();
      final user = User.fromJson(me.data as Map<String, dynamic>);
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } catch (e) {
      final msg = e is DioException ? apiErrorMessage(e) : MellowErrors.registerFailed;
      state = state.copyWith(isLoading: false, error: msg);
    }
  }

  Future<void> logout() async {
    final client = ref.read(apiClientProvider);
    await client.clearTokens();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  /// 开发模式：跳过登录直接进入，使用 mock 用户
  void devLogin() {
    state = AuthState(
      status: AuthStatus.authenticated,
      user: User(
        id: 'dev-1',
        username: '开发者',
        isActive: true,
      ),
    );
  }
}

final authProvider = NotifierProvider<AuthNotifier, AuthState>(
  AuthNotifier.new,
);
