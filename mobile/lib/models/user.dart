class User {
  final String id;
  final String username;
  final bool isActive;
  final String? accessToken;
  final String? refreshToken;

  const User({
    required this.id,
    required this.username,
    required this.isActive,
    this.accessToken,
    this.refreshToken,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as String,
        username: json['username'] as String,
        isActive: json['is_active'] as bool? ?? true,
        accessToken: json['access_token'] as String?,
        refreshToken: json['refresh_token'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'username': username,
        'is_active': isActive,
      };

  User copyWith({
    String? id,
    String? username,
    bool? isActive,
    String? accessToken,
    String? refreshToken,
  }) =>
      User(
        id: id ?? this.id,
        username: username ?? this.username,
        isActive: isActive ?? this.isActive,
        accessToken: accessToken ?? this.accessToken,
        refreshToken: refreshToken ?? this.refreshToken,
      );
}
