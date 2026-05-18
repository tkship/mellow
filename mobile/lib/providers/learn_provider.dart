import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/learning_stats.dart';
import '../services/api_client.dart';
import '../shared/constants/error_messages.dart';
import 'auth_provider.dart';

class LearnState {
  final LearningStats? stats;
  final VocabularyBook? vocabBook;
  final List<Mistake> mistakes;
  final bool isLoading;
  final String? error;
  final String range;

  const LearnState({
    this.stats,
    this.vocabBook,
    this.mistakes = const [],
    this.isLoading = false,
    this.error,
    this.range = 'month',
  });

  LearnState copyWith({
    LearningStats? stats,
    VocabularyBook? vocabBook,
    List<Mistake>? mistakes,
    bool? isLoading,
    String? error,
    String? range,
  }) =>
      LearnState(
        stats: stats ?? this.stats,
        vocabBook: vocabBook ?? this.vocabBook,
        mistakes: mistakes ?? this.mistakes,
        isLoading: isLoading ?? this.isLoading,
        error: error,
        range: range ?? this.range,
      );
}

class LearnNotifier extends Notifier<LearnState> {
  @override
  LearnState build() => const LearnState();

  Future<void> fetchStats() async {
    state = state.copyWith(isLoading: true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getStats(range: state.range);
      final stats = LearningStats.fromJson(
        res.data as Map<String, dynamic>,
      );
      state = state.copyWith(stats: stats, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: MellowErrors.loadFailed,
      );
    }
  }

  Future<void> setRange(String range) async {
    state = state.copyWith(range: range);
    await fetchStats();
  }

  Future<void> fetchVocab({String sort = 'recent'}) async {
    state = state.copyWith(isLoading: true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getVocabularyBook(sort: sort);
      final book = VocabularyBook.fromJson(
        res.data as Map<String, dynamic>,
      );
      state = state.copyWith(vocabBook: book, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: MellowErrors.loadVocabFailed,
      );
    }
  }

  Future<void> fetchMistakes() async {
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getMistakes();
      final data = res.data as Map<String, dynamic>;
      final list = (data['mistakes'] as List?)
              ?.cast<Map<String, dynamic>>()
              .map(Mistake.fromJson)
              .toList() ??
          [];
      state = state.copyWith(mistakes: list);
    } catch (_) {
      state = state.copyWith(error: MellowErrors.loadMistakesFailed);
    }
  }

  Future<void> deleteVocab(String word) async {
    try {
      final client = ref.read(apiClientProvider);
      await client.deleteVocabulary(word);
      await fetchVocab();
    } catch (_) {
      state = state.copyWith(error: MellowErrors.deleteVocabFailed);
    }
  }
}

final learnProvider = NotifierProvider<LearnNotifier, LearnState>(
  LearnNotifier.new,
);
