import 'api_client.dart';
import '../models/persona.dart';

class PersonaService {
  final ApiClient _client;

  PersonaService(this._client);

  Future<List<Persona>> listPresets() async {
    final res = await _client.get('/api/v1/personas');
    final list = res.data['personas'] as List<dynamic>;
    return list.map((j) => Persona.fromJson(j)).toList();
  }
}
