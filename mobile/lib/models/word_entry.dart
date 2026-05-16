class WordEntry {
  final String word;
  final String? phonetic;
  final String? partOfSpeech;
  final List<String> definitions;
  final List<String> examples;
  final List<String> synonyms;
  final String source;

  WordEntry({
    required this.word,
    this.phonetic,
    this.partOfSpeech,
    this.definitions = const [],
    this.examples = const [],
    this.synonyms = const [],
    this.source = '',
  });

  factory WordEntry.fromJson(Map<String, dynamic> json) => WordEntry(
        word: json['word'] ?? '',
        phonetic: json['phonetic'],
        partOfSpeech: json['part_of_speech'],
        definitions: List<String>.from(json['definitions'] ?? []),
        examples: List<String>.from(json['examples'] ?? []),
        synonyms: List<String>.from(json['synonyms'] ?? []),
        source: json['source'] ?? '',
      );
}
