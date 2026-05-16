enum MessageRole { user, assistant, system }

class ChatMessage {
  final String id;
  final String content;
  final MessageRole role;
  final DateTime timestamp;
  final bool isStreaming;

  ChatMessage({
    required this.id,
    required this.content,
    required this.role,
    DateTime? timestamp,
    this.isStreaming = false,
  }) : timestamp = timestamp ?? DateTime.now();

  bool get isUser => role == MessageRole.user;

  ChatMessage copyWith({String? content, bool? isStreaming}) => ChatMessage(
        id: id,
        content: content ?? this.content,
        role: role,
        timestamp: timestamp,
        isStreaming: isStreaming ?? this.isStreaming,
      );
}
