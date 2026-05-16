import 'api_client.dart';
import '../models/word_entry.dart';

class KnowledgeService {
  final ApiClient _client;

  KnowledgeService(this._client);

  Future<WordEntry?> lookup(String word) async {
    try {
      final res = await _client.get(
        '/api/v1/knowledge/lookup',
        queryParameters: {'word': word},
      );
      return WordEntry.fromJson(res.data);
    } catch (_) {
      return null;
    }
  }
}
