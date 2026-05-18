class WordEntry {
  final String word;
  final String? phonetic;
  final String? partOfSpeech;
  final List<String> definitions;
  final List<String> examples;
  final List<String> synonyms;
  final String? source;
  final String? addedAt;

  const WordEntry({
    required this.word,
    this.phonetic,
    this.partOfSpeech,
    this.definitions = const [],
    this.examples = const [],
    this.synonyms = const [],
    this.source,
    this.addedAt,
  });

  factory WordEntry.fromJson(Map<String, dynamic> json) => WordEntry(
        word: json['word'] as String,
        phonetic: json['phonetic'] as String?,
        partOfSpeech: json['part_of_speech'] as String?,
        definitions: (json['definitions'] as List?)?.cast<String>() ?? [],
        examples: (json['examples'] as List?)?.cast<String>() ?? [],
        synonyms: (json['synonyms'] as List?)?.cast<String>() ?? [],
        source: json['source'] as String?,
        addedAt: json['added_at'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'word': word,
        if (phonetic != null) 'phonetic': phonetic,
        if (partOfSpeech != null) 'part_of_speech': partOfSpeech,
        'definitions': definitions,
        'examples': examples,
        'synonyms': synonyms,
      };
}
