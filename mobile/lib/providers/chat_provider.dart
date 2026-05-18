import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/message.dart';
import '../services/api_client.dart';
import '../shared/constants/error_messages.dart';
import 'auth_provider.dart';

class ChatState {
  final List<Message> messages;
  final bool isLoading;
  final bool isStreaming;
  final bool isLoadingHistory;
  final String? nextCursor;
  final String? error;
  final String? streamBuffer;

  const ChatState({
    this.messages = const [],
    this.isLoading = false,
    this.isStreaming = false,
    this.isLoadingHistory = false,
    this.nextCursor,
    this.error,
    this.streamBuffer,
  });

  ChatState copyWith({
    List<Message>? messages,
    bool? isLoading,
    bool? isStreaming,
    bool? isLoadingHistory,
    String? nextCursor,
    String? error,
    String? streamBuffer,
    bool clearError = false,
  }) =>
      ChatState(
        messages: messages ?? this.messages,
        isLoading: isLoading ?? this.isLoading,
        isStreaming: isStreaming ?? this.isStreaming,
        isLoadingHistory: isLoadingHistory ?? this.isLoadingHistory,
        nextCursor: nextCursor ?? this.nextCursor,
        error: clearError ? null : (error ?? this.error),
        streamBuffer: streamBuffer ?? this.streamBuffer,
      );
}

class ChatNotifier extends Notifier<ChatState> {
  StreamSubscription<Map<String, dynamic>>? _streamSub;

  @override
  ChatState build() {
    ref.onDispose(() => _streamSub?.cancel());
    return const ChatState();
  }

  /// 发送消息 — SSE 流式
  Future<void> sendMessage({
    required String personaId,
    required String content,
  }) async {
    final client = ref.read(apiClientProvider);
    final token = await client.accessToken;

    // 添加用户消息
    final userMsg = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      role: MessageRole.user,
      timestamp: DateTime.now(),
    );
    state = state.copyWith(
      messages: [...state.messages, userMsg],
      isLoading: true,
      clearError: true,
    );

    // 创建 AI 流式消息占位
    final aiMsgId = 'ai_${DateTime.now().millisecondsSinceEpoch}';
    final aiMsg = Message(
      id: aiMsgId,
      content: '',
      role: MessageRole.assistant,
      timestamp: DateTime.now(),
      isStreaming: true,
    );
    state = state.copyWith(
      messages: [...state.messages, aiMsg],
      isStreaming: true,
      streamBuffer: '',
    );

    try {
      final stream = client.streamChat(
        personaId: personaId,
        message: content,
        token: token,
      );

      // Cancel any existing stream to prevent race conditions
      _streamSub?.cancel();
      _streamSub = stream.listen(
        (data) {
          if (data['done'] == true) {
            // 流式完成
            final msgs = state.messages.map((m) {
              if (m.id == aiMsgId) {
                return m.copyWith(isStreaming: false);
              }
              return m;
            }).toList();
            state = state.copyWith(
              messages: msgs,
              isStreaming: false,
              isLoading: false,
            );
            return;
          }

          final token = data['token'] as String?;
          if (token != null) {
            final buffer = (state.streamBuffer ?? '') + token;
            final msgs = state.messages.map((m) {
              if (m.id == aiMsgId) {
                return m.copyWith(content: buffer);
              }
              return m;
            }).toList();
            state = state.copyWith(messages: msgs, streamBuffer: buffer);
          }
        },
        onError: (e) {
          _streamSub?.cancel();
          _streamSub = null;
          state = state.copyWith(
            isLoading: false,
            isStreaming: false,
            error: MellowErrors.connectionLost,
          );
        },
        onDone: () {
          _streamSub = null;
          state = state.copyWith(isLoading: false, isStreaming: false);
        },
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        isStreaming: false,
        error: MellowErrors.sendFailed,
      );
    }
  }

  /// 同步发送兜底
  Future<void> sendMessageSync({
    required String personaId,
    required String content,
  }) async {
    final client = ref.read(apiClientProvider);

    final userMsg = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      role: MessageRole.user,
      timestamp: DateTime.now(),
    );
    state = state.copyWith(
      messages: [...state.messages, userMsg],
      isLoading: true,
      clearError: true,
    );

    try {
      final res = await client.sendMessage(personaId, content);
      final data = res.data as Map<String, dynamic>;
      final aiMsg = Message(
        id: 'ai_${DateTime.now().millisecondsSinceEpoch}',
        content: data['reply'] as String? ?? '',
        role: MessageRole.assistant,
        timestamp: DateTime.now(),
      );
      state = state.copyWith(
        messages: [...state.messages, aiMsg],
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: MellowErrors.sendFailed,
      );
    }
  }

  /// 加载聊天历史（首次进入页面）
  Future<void> loadHistory(String personaId) async {
    if (state.isLoadingHistory) return;

    state = state.copyWith(isLoadingHistory: true, clearError: true);

    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getChatHistory(personaId);
      final data = res.data as Map<String, dynamic>;
      final msgs = (data['messages'] as List?)
              ?.map((m) => Message.fromJson(m as Map<String, dynamic>))
              .toList() ??
          [];

      // 历史消息按正序排列（旧消息在上，新消息在下）
      // 后端返回的是倒序，所以需要反转
      final orderedMsgs = msgs.reversed.toList();

      state = state.copyWith(
        messages: orderedMsgs,
        isLoadingHistory: false,
        nextCursor: data['next_cursor'] as String?,
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingHistory: false,
        error: MellowErrors.loadFailed,
      );
    }
  }

  /// 加载更多历史消息（上滑加载）
  Future<void> loadMoreHistory(String personaId) async {
    if (state.isLoadingHistory || state.nextCursor == null) return;

    state = state.copyWith(isLoadingHistory: true);

    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getChatHistory(
        personaId,
        cursor: state.nextCursor,
      );
      final data = res.data as Map<String, dynamic>;
      final msgs = (data['messages'] as List?)
              ?.map((m) => Message.fromJson(m as Map<String, dynamic>))
              .toList() ??
          [];

      // 新加载的更早消息放在列表顶部（反转后 prepend）
      final orderedMsgs = msgs.reversed.toList();
      state = state.copyWith(
        messages: [...orderedMsgs, ...state.messages],
        isLoadingHistory: false,
        nextCursor: data['next_cursor'] as String?,
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingHistory: false,
        error: MellowErrors.loadFailed,
      );
    }
  }

  /// 获取快捷短语
  Future<List<String>> fetchPhrases(String personaId) async {
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getPhrases(personaId);
      final data = res.data as Map<String, dynamic>;
      return (data['phrases'] as List?)?.cast<String>() ?? [];
    } catch (e) {
      debugPrint('Failed to fetch phrases: $e');
      return [];
    }
  }

  /// 收藏/取消收藏消息 —— 乐观更新 + API 持久化
  Future<void> toggleFavorite(String messageId, String personaId) async {
    // 乐观更新
    final originalMsgs = List<Message>.from(state.messages);
    final msgs = state.messages.map((m) {
      if (m.id == messageId) {
        return m.copyWith(isFavorite: !m.isFavorite);
      }
      return m;
    }).toList();
    state = state.copyWith(messages: msgs, clearError: true);

    try {
      final client = ref.read(apiClientProvider);
      await client.toggleMessageFavorite(messageId, personaId);
    } catch (e) {
      // 回滚并显示错误
      state = state.copyWith(
        messages: originalMsgs,
        error: MellowErrors.favoriteFailed,
      );
    }
  }

  /// 删除消息 —— 乐观更新 + API 持久化
  Future<void> deleteMessage(String messageId, String personaId) async {
    // 乐观更新
    final originalMsgs = List<Message>.from(state.messages);
    final msgs = state.messages.where((m) => m.id != messageId).toList();
    state = state.copyWith(messages: msgs, clearError: true);

    try {
      final client = ref.read(apiClientProvider);
      await client.deleteMessage(messageId, personaId);
    } catch (e) {
      // 回滚并显示错误
      state = state.copyWith(
        messages: originalMsgs,
        error: MellowErrors.deleteFailed,
      );
    }
  }

  void clearError() {
    state = state.copyWith(clearError: true);
  }
}

final chatProvider = NotifierProvider<ChatNotifier, ChatState>(
  ChatNotifier.new,
);
