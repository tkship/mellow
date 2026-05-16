class LanguageStyle {
  final String tone;
  final List<String> traits;

  LanguageStyle({this.tone = '', this.traits = const []});

  factory LanguageStyle.fromJson(Map<String, dynamic> json) => LanguageStyle(
        tone: json['tone'] ?? '',
        traits: List<String>.from(json['traits'] ?? []),
      );
}

class TeachingStyle {
  final String approach;
  final double strictness;
  final String correctionFrequency;

  TeachingStyle({
    this.approach = '',
    this.strictness = 0.5,
    this.correctionFrequency = 'major_only',
  });

  factory TeachingStyle.fromJson(Map<String, dynamic> json) => TeachingStyle(
        approach: json['approach'] ?? '',
        strictness: (json['strictness'] ?? 0.5).toDouble(),
        correctionFrequency: json['correction_frequency'] ?? 'major_only',
      );
}

class Persona {
  final String id;
  final String name;
  final String role;
  final LanguageStyle languageStyle;
  final TeachingStyle teachingStyle;
  final String intimacyLevel;
  final String? voiceId;
  final bool isPreset;

  Persona({
    required this.id,
    required this.name,
    required this.role,
    required this.languageStyle,
    required this.teachingStyle,
    this.intimacyLevel = 'casual',
    this.voiceId,
    this.isPreset = false,
  });

  factory Persona.fromJson(Map<String, dynamic> json) => Persona(
        id: json['id'] ?? '',
        name: json['name'] ?? '',
        role: json['role'] ?? '',
        languageStyle: LanguageStyle.fromJson(json['language_style'] ?? {}),
        teachingStyle: TeachingStyle.fromJson(json['teaching_style'] ?? {}),
        intimacyLevel: json['intimacy_level'] ?? 'casual',
        voiceId: json['voice_id'],
        isPreset: json['is_preset'] ?? false,
      );

  String get roleEmoji {
    switch (role) {
      case 'girlfriend': return '💕';
      case 'strict teacher': return '📚';
      case 'study buddy': return '🤝';
      case 'humorous friend': return '😄';
      default: return '🌟';
    }
  }
}
