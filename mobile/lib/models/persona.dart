class Persona {
  final String id;
  final String name;
  final String role;
  final String? roleEmoji;
  final LanguageStyle languageStyle;
  final TeachingStyle teachingStyle;
  final String? intimacyLevel;
  final List<int>? interactionRhythm;
  final double? emotionalSensitivity;
  final String? systemPromptTemplate;
  final bool isPreset;
  final String? createdBy;
  final String? voiceId;

  const Persona({
    required this.id,
    required this.name,
    required this.role,
    this.roleEmoji,
    required this.languageStyle,
    required this.teachingStyle,
    this.intimacyLevel,
    this.interactionRhythm,
    this.emotionalSensitivity,
    this.systemPromptTemplate,
    required this.isPreset,
    this.createdBy,
    this.voiceId,
  });

  factory Persona.fromJson(Map<String, dynamic> json) {
    return Persona(
      id: json['id'] as String,
      name: json['name'] as String,
      role: json['role'] as String,
      roleEmoji: json['role_emoji'] as String?,
      languageStyle: LanguageStyle.fromJson(
        json['language_style'] as Map<String, dynamic>,
      ),
      teachingStyle: TeachingStyle.fromJson(
        json['teaching_style'] as Map<String, dynamic>,
      ),
      intimacyLevel: json['intimacy_level'] as String?,
      interactionRhythm:
          (json['interaction_rhythm'] as List?)?.cast<int>(),
      emotionalSensitivity: (json['emotional_sensitivity'] as num?)?.toDouble(),
      systemPromptTemplate: json['system_prompt_template'] as String?,
      isPreset: json['is_preset'] as bool? ?? false,
      createdBy: json['created_by'] as String?,
      voiceId: json['voice_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'role': role,
        'language_style': languageStyle.toJson(),
        'teaching_style': teachingStyle.toJson(),
        'is_preset': isPreset,
        if (voiceId != null) 'voice_id': voiceId,
      };
}

class LanguageStyle {
  final String tone;
  final List<String> traits;

  const LanguageStyle({required this.tone, required this.traits});

  factory LanguageStyle.fromJson(Map<String, dynamic> json) => LanguageStyle(
        tone: json['tone'] as String? ?? '',
        traits: (json['traits'] as List?)?.cast<String>() ?? [],
      );

  Map<String, dynamic> toJson() => {'tone': tone, 'traits': traits};
}

class TeachingStyle {
  final String approach;
  final double strictness;
  final String correctionFrequency;

  const TeachingStyle({
    required this.approach,
    required this.strictness,
    required this.correctionFrequency,
  });

  factory TeachingStyle.fromJson(Map<String, dynamic> json) => TeachingStyle(
        approach: json['approach'] as String? ?? '',
        strictness: (json['strictness'] as num?)?.toDouble() ?? 0.5,
        correctionFrequency: json['correction_frequency'] as String? ?? '',
      );

  Map<String, dynamic> toJson() => {
        'approach': approach,
        'strictness': strictness,
        'correction_frequency': correctionFrequency,
      };
}
