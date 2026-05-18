import 'word_entry.dart';

export 'word_entry.dart';

class LearningStats {
  final String cefrLevel;
  final int vocabCount;
  final int learningDays;
  final int checkInCount;
  final int totalMessages;
  final List<String> weakAreas;
  final List<CefrProgress> cefrProgress;
  final String? range;

  const LearningStats({
    required this.cefrLevel,
    required this.vocabCount,
    required this.learningDays,
    required this.checkInCount,
    required this.totalMessages,
    required this.weakAreas,
    required this.cefrProgress,
    this.range,
  });

  factory LearningStats.fromJson(Map<String, dynamic> json) => LearningStats(
        cefrLevel: json['cefr_level'] as String? ?? 'A0',
        vocabCount: json['vocabulary_size'] as int? ?? 0,
        learningDays: json['learning_days'] as int? ?? 0,
        checkInCount: json['check_in_count'] as int? ?? 0,
        totalMessages: json['total_messages'] as int? ?? 0,
        weakAreas:
            (json['weak_areas'] as List?)?.cast<String>() ?? [],
        cefrProgress: (json['cefr_progress'] as List?)
                ?.cast<Map<String, dynamic>>()
                .map(CefrProgress.fromJson)
                .toList() ??
            [],
        range: json['range'] as String?,
      );
}

class CefrProgress {
  final String date;
  final String level;
  final double score;

  const CefrProgress({
    required this.date,
    required this.level,
    required this.score,
  });

  factory CefrProgress.fromJson(Map<String, dynamic> json) => CefrProgress(
        date: json['date'] as String? ?? '',
        level: json['level'] as String? ?? 'A0',
        score: (json['score'] as num?)?.toDouble() ?? 0.0,
      );
}

class VocabularyBook {
  final int total;
  final List<VocabGroup> groups;

  const VocabularyBook({required this.total, required this.groups});

  factory VocabularyBook.fromJson(Map<String, dynamic> json) => VocabularyBook(
        total: json['total'] as int? ?? 0,
        groups: (json['groups'] as List?)
                ?.cast<Map<String, dynamic>>()
                .map(VocabGroup.fromJson)
                .toList() ??
            [],
      );
}

class VocabGroup {
  final String letter;
  final int count;
  final List<WordEntry> words;

  const VocabGroup({
    required this.letter,
    required this.count,
    required this.words,
  });

  factory VocabGroup.fromJson(Map<String, dynamic> json) => VocabGroup(
        letter: json['letter'] as String? ?? '',
        count: json['count'] as int? ?? 0,
        words: (json['words'] as List?)
                ?.cast<Map<String, dynamic>>()
                .map(WordEntry.fromJson)
                .toList() ??
            [],
      );
}

class Mistake {
  final String wordOrRule;
  final String mistakeType;
  final String context;
  final String correction;
  final String timestamp;

  const Mistake({
    required this.wordOrRule,
    required this.mistakeType,
    required this.context,
    required this.correction,
    required this.timestamp,
  });

  factory Mistake.fromJson(Map<String, dynamic> json) => Mistake(
        wordOrRule: json['word_or_rule'] as String? ?? '',
        mistakeType: json['mistake_type'] as String? ?? '',
        context: json['context'] as String? ?? '',
        correction: json['correction'] as String? ?? '',
        timestamp: json['timestamp'] as String? ?? '',
      );
}

class ProfileInfo {
  final String cefrLevel;
  final int vocabularySize;
  final int knownWordsCount;
  final List<String> weakAreas;
  final List<String> completedLessons;
  final String? summary;

  const ProfileInfo({
    required this.cefrLevel,
    required this.vocabularySize,
    required this.knownWordsCount,
    required this.weakAreas,
    required this.completedLessons,
    this.summary,
  });

  factory ProfileInfo.fromJson(Map<String, dynamic> json) => ProfileInfo(
        cefrLevel: json['cefr_level'] as String? ?? 'A0',
        vocabularySize: json['vocabulary_size'] as int? ?? 0,
        knownWordsCount: json['known_words_count'] as int? ?? 0,
        weakAreas:
            (json['weak_areas'] as List?)?.cast<String>() ?? [],
        completedLessons:
            (json['completed_lessons'] as List?)?.cast<String>() ?? [],
        summary: json['summary'] as String?,
      );
}
