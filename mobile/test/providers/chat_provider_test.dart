import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:mellow/models/message.dart';
import 'package:mellow/providers/auth_provider.dart';
import 'package:mellow/providers/chat_provider.dart';
import 'package:mellow/services/api_client.dart';

class MockApiClient extends Mock implements ApiClient {}

/// Creates a minimal SSE stream that mimics server-sent events.
Stream<Map<String, dynamic>> _fakeSseStream(
  List<Map<String, dynamic>> events,
) =>
    Stream.fromIterable(events);

void main() {
  late ProviderContainer container;
  late MockApiClient mockApiClient;
  late ChatNotifier notifier;

  setUp(() {
    mockApiClient = MockApiClient();
    container = ProviderContainer(
      overrides: [
        apiClientProvider.overrideWith((ref) => mockApiClient),
      ],
    );
    notifier = container.read(chatProvider.notifier);
  });

  tearDown(() {
    container.dispose();
  });

  group('sendMessage()', () {
    setUp(() {
      // Common setup: a valid token always available.
      when(() => mockApiClient.accessToken)
          .thenAnswer((_) async => 'test-token');
    });

    test('adds user message to list immediately', () async {
      when(
        () => mockApiClient.streamChat(
          personaId: any(named: 'personaId'),
          message: any(named: 'message'),
          token: any(named: 'token'),
        ),
      ).thenAnswer((_) => _fakeSseStream([
            {'done': true},
          ]));

      await notifier.sendMessage(personaId: 'p1', content: 'Hello');

      final messages = notifier.state.messages;
      expect(messages.length, greaterThanOrEqualTo(2));
      final userMsg = messages.firstWhere((m) => m.role == MessageRole.user);
      expect(userMsg.content, 'Hello');
    });

    test('SSE stream events append tokens to the last AI message', () async {
      when(
        () => mockApiClient.streamChat(
          personaId: any(named: 'personaId'),
          message: any(named: 'message'),
          token: any(named: 'token'),
        ),
      ).thenAnswer((_) => _fakeSseStream([
            {'token': 'Hi'},
            {'token': ' there'},
            {'token': '!'},
            {'done': true},
          ]));

      await notifier.sendMessage(personaId: 'p1', content: 'Hi');

      // Give time for the stream listener to process events.
      await Future<void>.delayed(const Duration(milliseconds: 10));

      final aiMsg = notifier.state.messages
          .firstWhere((m) => m.role == MessageRole.assistant);
      expect(aiMsg.content, 'Hi there!');
      expect(aiMsg.isStreaming, isFalse);
      expect(notifier.state.isStreaming, isFalse);
    });

    test('SSE [DONE] event marks message as not streaming', () async {
      when(
        () => mockApiClient.streamChat(
          personaId: any(named: 'personaId'),
          message: any(named: 'message'),
          token: any(named: 'token'),
        ),
      ).thenAnswer((_) => _fakeSseStream([
            {'token': 'Reply'},
            {'done': true},
          ]));

      await notifier.sendMessage(personaId: 'p1', content: 'Query');

      await Future<void>.delayed(const Duration(milliseconds: 10));

      final aiMsg = notifier.state.messages
          .firstWhere((m) => m.role == MessageRole.assistant);
      expect(aiMsg.isStreaming, isFalse);
      expect(notifier.state.isStreaming, isFalse);
    });
  });

  group('toggleFavorite()', () {
    test('toggles isFavorite on correct message', () async {
      when(() => mockApiClient.accessToken)
          .thenAnswer((_) async => 'test-token');
      when(
        () => mockApiClient.streamChat(
          personaId: any(named: 'personaId'),
          message: any(named: 'message'),
          token: any(named: 'token'),
        ),
      ).thenAnswer((_) => _fakeSseStream([
            {'done': true},
          ]));
      when(
        () => mockApiClient.toggleMessageFavorite(
          any(named: 'messageId'),
          any(named: 'personaId'),
        ),
      ).thenAnswer((_) async => {});

      await notifier.sendMessage(personaId: 'p1', content: 'Fav test');

      final msgId = notifier.state.messages.first.id;
      expect(
        notifier.state.messages.firstWhere((m) => m.id == msgId).isFavorite,
        isFalse,
      );

      await notifier.toggleFavorite(msgId, 'p1');

      expect(
        notifier.state.messages.firstWhere((m) => m.id == msgId).isFavorite,
        isTrue,
      );

      await notifier.toggleFavorite(msgId, 'p1');

      expect(
        notifier.state.messages.firstWhere((m) => m.id == msgId).isFavorite,
        isFalse,
      );
    });
  });

  group('deleteMessage()', () {
    test('removes message from list', () async {
      when(() => mockApiClient.accessToken)
          .thenAnswer((_) async => 'test-token');
      when(
        () => mockApiClient.streamChat(
          personaId: any(named: 'personaId'),
          message: any(named: 'message'),
          token: any(named: 'token'),
        ),
      ).thenAnswer((_) => _fakeSseStream([
            {'done': true},
          ]));
      when(
        () => mockApiClient.deleteMessage(
          any(named: 'messageId'),
          any(named: 'personaId'),
        ),
      ).thenAnswer((_) async => {});

      await notifier.sendMessage(personaId: 'p1', content: 'Delete me');

      final userMsg =
          notifier.state.messages.firstWhere((m) => m.role == MessageRole.user);
      final initialCount = notifier.state.messages.length;

      await notifier.deleteMessage(userMsg.id, 'p1');

      expect(notifier.state.messages.length, initialCount - 1);
      expect(
        notifier.state.messages.any((m) => m.id == userMsg.id),
        isFalse,
      );
    });
  });

  group('clearError()', () {
    test('clears any existing error in state', () async {
      // Manually set an error state via copyWith (simulating an error).
      // We can set state directly because we have access to the notifier.
      // The state setter is available on Notifier (Riverpod 2.x).
      notifier.state = notifier.state.copyWith(error: 'Something went wrong');
      expect(notifier.state.error, 'Something went wrong');

      notifier.clearError();

      expect(notifier.state.error, isNull);
    });
  });
}
