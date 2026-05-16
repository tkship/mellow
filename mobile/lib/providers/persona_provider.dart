import 'package:flutter/foundation.dart';

import '../models/persona.dart';
import '../services/api_client.dart';
import '../services/persona_service.dart';

class PersonaProvider extends ChangeNotifier {
  final ApiClient _client = ApiClient();
  late final PersonaService _service = PersonaService(_client);

  List<Persona> _presets = [];
  Persona? _selected;
  bool _loading = false;

  List<Persona> get presets => _presets;
  Persona? get selected => _selected;

  Future<void> loadPresets() async {
    _loading = true;
    notifyListeners();
    try {
      _presets = await _service.listPresets();
    } catch (_) {}
    _loading = false;
    notifyListeners();
  }

  void selectPersona(Persona persona) {
    _selected = persona;
    notifyListeners();
  }
}
