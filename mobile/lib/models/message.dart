enum MessageRole { user, assistant }

class Message {
  final String id;
  final String content;
  final MessageRole role;
  final DateTime timestamp;
  final bool isFavorite;
  final bool isStreaming;

  const Message({
    required this.id,
    required this.content,
    required this.role,
    required this.timestamp,
    this.isFavorite = false,
    this.isStreaming = false,
  });

  factory Message.fromJson(Map<String, dynamic> json) => Message(
        id: json['id'] as String? ?? DateTime.now().millisecondsSinceEpoch.toString(),
        content: json['content'] as String? ?? '',
        role: _parseRole(json['role'] as String?),
        timestamp: json['timestamp'] != null
            ? DateTime.parse(json['timestamp'] as String)
            : DateTime.now(),
        isFavorite: json['is_favorite'] as bool? ?? false,
      );

  static MessageRole _parseRole(String? role) {
    return role == 'assistant' ? MessageRole.assistant : MessageRole.user;
  }

  Message copyWith({
    String? id,
    String? content,
    MessageRole? role,
    DateTime? timestamp,
    bool? isFavorite,
    bool? isStreaming,
  }) =>
      Message(
        id: id ?? this.id,
        content: content ?? this.content,
        role: role ?? this.role,
        timestamp: timestamp ?? this.timestamp,
        isFavorite: isFavorite ?? this.isFavorite,
        isStreaming: isStreaming ?? this.isStreaming,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'content': content,
        'role': role == MessageRole.assistant ? 'assistant' : 'user',
        'timestamp': timestamp.toIso8601String(),
        'is_favorite': isFavorite,
      };
}
