import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/persona.dart';
import '../shared/constants/error_messages.dart';
import 'auth_provider.dart';

/// 角色列表状态
class PersonaState {
  final List<Persona> personas;
  final Persona? selected;
  final bool isLoading;
  final String? error;

  const PersonaState({
    this.personas = const [],
    this.selected,
    this.isLoading = false,
    this.error,
  });

  PersonaState copyWith({
    List<Persona>? personas,
    Persona? selected,
    bool? isLoading,
    String? error,
    bool clearError = false,
    bool clearSelected = false,
  }) =>
      PersonaState(
        personas: personas ?? this.personas,
        selected: clearSelected ? null : (selected ?? this.selected),
        isLoading: isLoading ?? this.isLoading,
        error: clearError ? null : (error ?? this.error),
      );
}

/// 角色状态管理
class PersonaNotifier extends Notifier<PersonaState> {
  @override
  PersonaState build() => const PersonaState();

  /// 获取角色列表
  Future<void> fetchPersonas() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getPersonas();
      final data = res.data as Map<String, dynamic>;
      final personas = (data['personas'] as List?)
          ?.cast<Map<String, dynamic>>()
          .map(Persona.fromJson)
          .toList() ?? [];
      state = state.copyWith(personas: personas, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: MellowErrors.loadPersonasFailed,
      );
    }
  }

  /// 选中角色
  void selectPersona(Persona persona) {
    state = state.copyWith(selected: persona);
  }

  /// 获取角色详情
  Future<void> fetchDetail(String id) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getPersonaDetail(id);
      final persona = Persona.fromJson(res.data as Map<String, dynamic>);
      state = state.copyWith(selected: persona, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: MellowErrors.loadPersonaDetailFailed,
      );
    }
  }
}

/// 角色 Provider
final personaProvider = NotifierProvider<PersonaNotifier, PersonaState>(
  PersonaNotifier.new,
);
