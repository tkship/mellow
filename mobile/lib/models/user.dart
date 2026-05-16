class User {
  final String id;
  final String username;
  final bool isActive;

  User({required this.id, required this.username, this.isActive = true});

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] ?? '',
        username: json['username'] ?? '',
        isActive: json['is_active'] ?? true,
      );
}

class Token {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;

  Token({
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'bearer',
    required this.expiresIn,
  });

  factory Token.fromJson(Map<String, dynamic> json) => Token(
        accessToken: json['access_token'] ?? '',
        refreshToken: json['refresh_token'] ?? '',
        tokenType: json['token_type'] ?? 'bearer',
        expiresIn: json['expires_in'] ?? 86400,
      );
}
