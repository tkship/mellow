import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import 'package:mellow/models/message.dart';
import 'package:mellow/shared/widgets/message_bubble.dart';
import 'package:mellow/theme/colors.dart';
import 'package:mellow/theme/shadcn_theme.dart';

/// Wraps [child] in the minimal widget tree needed by [MessageBubble]:
/// [ShadApp] for [ShadTheme] and a [Scaffold] for layout.
Widget _wrapBubble(Widget child) {
  return ShadApp(
    theme: mellowLightTheme,
    home: Scaffold(body: Center(child: child)),
  );
}

void main() {
  const testContent = 'Hello, this is a test message.';
  final testTimestamp = DateTime(2025, 5, 17, 12, 0);

  group('MessageBubble', () {
    // ── AI message alignment & style ──

    testWidgets('AI message renders left-aligned with correct style',
        (tester) async {
      final msg = Message(
        id: 'ai-1',
        content: testContent,
        role: MessageRole.assistant,
        timestamp: testTimestamp,
      );

      await tester.pumpWidget(_wrapBubble(MessageBubble(message: msg)));
      await tester.pumpAndSettle();

      // The message text is rendered
      expect(find.text(testContent), findsOneWidget);

      // AI avatar should show the robot emoji
      expect(find.text('🤖'), findsOneWidget);

      // AI bubble uses muted background (not brandGreen)
      final greenContainers = find.byWidgetPredicate(
        (w) =>
            w is Container &&
            w.decoration is BoxDecoration &&
            (w.decoration! as BoxDecoration).color == MellowColors.brandGreen,
      );
      expect(greenContainers, findsNothing);
    });

    // ── User message alignment & style ──

    testWidgets('User message renders right-aligned with correct style',
        (tester) async {
      final msg = Message(
        id: 'u-1',
        content: testContent,
        role: MessageRole.user,
        timestamp: testTimestamp,
      );

      await tester.pumpWidget(_wrapBubble(MessageBubble(message: msg)));
      await tester.pumpAndSettle();

      expect(find.text(testContent), findsOneWidget);

      // User avatar should show a person icon
      expect(find.byIcon(Icons.person), findsOneWidget);

      // User bubble uses brandGreen background (not the CircleAvatar, which
      // also has brandGreen — exclude BoxShape.circle to differentiate)
      final greenContainers = find.byWidgetPredicate(
        (w) =>
            w is Container &&
            w.decoration is BoxDecoration &&
            (w.decoration! as BoxDecoration).color == MellowColors.brandGreen &&
            (w.decoration! as BoxDecoration).shape != BoxShape.circle,
      );
      expect(greenContainers, findsOneWidget);
    });

    // ── Avatar ──

    testWidgets('AI message shows avatar with robot emoji', (tester) async {
      final msg = Message(
        id: 'ai-2',
        content: 'AI says hi',
        role: MessageRole.assistant,
        timestamp: testTimestamp,
      );

      await tester.pumpWidget(_wrapBubble(MessageBubble(message: msg)));
      await tester.pumpAndSettle();

      // CircleAvatar for AI has robot emoji
      expect(find.text('🤖'), findsOneWidget);
      // No person icon for AI
      expect(find.byIcon(Icons.person), findsNothing);
    });

    // ── Favorite star ──

    testWidgets('shows favorite star icon when isFavorite is true',
        (tester) async {
      final msg = Message(
        id: 'fav-1',
        content: 'Starred message',
        role: MessageRole.assistant,
        timestamp: testTimestamp,
        isFavorite: true,
      );

      await tester.pumpWidget(_wrapBubble(MessageBubble(message: msg)));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.star), findsOneWidget);
    });

    testWidgets('hides favorite star icon when isFavorite is false',
        (tester) async {
      final msg = Message(
        id: 'nofav-1',
        content: 'Unstarred message',
        role: MessageRole.assistant,
        timestamp: testTimestamp,
        isFavorite: false,
      );

      await tester.pumpWidget(_wrapBubble(MessageBubble(message: msg)));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.star), findsNothing);
    });

    // ── Streaming indicator ──

    testWidgets('shows typing indicator when isStreaming=true and content empty',
        (tester) async {
      final msg = Message(
        id: 'stream-1',
        content: '',
        role: MessageRole.assistant,
        timestamp: testTimestamp,
        isStreaming: true,
      );

      await tester.pumpWidget(_wrapBubble(MessageBubble(message: msg)));
      // Pump frames so the AnimationController starts and dots render.
      // Use pump() instead of pumpAndSettle() because the animation repeats
      // forever and never settles.
      await tester.pump(const Duration(milliseconds: 100));
      await tester.pump(const Duration(milliseconds: 100));

      // No text content when streaming with empty content
      expect(find.text(''), findsNothing);

      // The typing indicator renders animated dot containers (circles).
      // Together with the CircleAvatar there should be at least 4 circle
      // containers: 3 typing dots (8x8) + 1 avatar circle (32x32).
      final circleContainers = find.byWidgetPredicate(
        (w) =>
            w is Container &&
            w.decoration is BoxDecoration &&
            (w.decoration! as BoxDecoration).shape == BoxShape.circle,
      );
      expect(circleContainers, findsAtLeastNWidgets(4));
    });

    // ── Message content display ──

    testWidgets('displays message content text correctly', (tester) async {
      const longText = 'This is a longer message to verify the text content '
          'is rendered properly inside the bubble.';

      final msg = Message(
        id: 'text-1',
        content: longText,
        role: MessageRole.user,
        timestamp: testTimestamp,
      );

      await tester.pumpWidget(_wrapBubble(MessageBubble(message: msg)));
      await tester.pumpAndSettle();

      expect(find.text(longText), findsOneWidget);
    });

    // ── Edge case: streaming with content ──

    testWidgets('shows content text when streaming with non-empty content',
        (tester) async {
      final msg = Message(
        id: 'stream-2',
        content: 'Partial response...',
        role: MessageRole.assistant,
        timestamp: testTimestamp,
        isStreaming: true,
      );

      await tester.pumpWidget(_wrapBubble(MessageBubble(message: msg)));
      await tester.pumpAndSettle();

      // When content is non-empty, text is shown instead of typing indicator
      expect(find.text('Partial response...'), findsOneWidget);
    });
  });
}
