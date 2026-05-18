import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:mellow/models/persona.dart';
import 'package:mellow/providers/auth_provider.dart';
import 'package:mellow/providers/persona_provider.dart';
import 'package:mellow/services/api_client.dart';

class MockApiClient extends Mock implements ApiClient {}

Persona createMockPersona({
  String id = '1',
  String name = 'Test Persona',
  String role = 'teacher',
  String? roleEmoji,
  LanguageStyle? languageStyle,
  TeachingStyle? teachingStyle,
  bool isPreset = true,
}) {
  return Persona(
    id: id,
    name: name,
    role: role,
    roleEmoji: roleEmoji,
    languageStyle:
        languageStyle ?? const LanguageStyle(tone: 'friendly', traits: ['patient']),
    teachingStyle: teachingStyle ??
        const TeachingStyle(
          approach: 'conversational',
          strictness: 0.5,
          correctionFrequency: 'occasional',
        ),
    isPreset: isPreset,
  );
}

/// Creates a minimal Dio [Response] with the given [data] payload.
Response<dynamic> _mockResponse(dynamic data) {
  return Response<dynamic>(
    requestOptions: RequestOptions(),
    data: data,
  );
}

void main() {
  late ProviderContainer container;
  late MockApiClient mockClient;

  setUp(() {
    mockClient = MockApiClient();
    container = ProviderContainer(
      overrides: [apiClientProvider.overrideWithValue(mockClient)],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('PersonaProvider', () {
    // ── fetchPersonas ──

    test('fetchPersonas() loads persona list and sets state', () async {
      when(() => mockClient.getPersonas()).thenAnswer(
        (_) async => _mockResponse({
          'personas': [
            {
              'id': '1',
              'name': 'Alice',
              'role': 'teacher',
              'language_style': {'tone': 'warm', 'traits': ['kind']},
              'teaching_style': {
                'approach': 'gentle',
                'strictness': 0.3,
                'correction_frequency': 'often',
              },
              'is_preset': true,
            },
            {
              'id': '2',
              'name': 'Bob',
              'role': 'friend',
              'language_style': {'tone': 'casual', 'traits': ['funny']},
              'teaching_style': {
                'approach': 'direct',
                'strictness': 0.7,
                'correction_frequency': 'always',
              },
              'is_preset': false,
            },
          ],
        }),
      );

      await container.read(personaProvider.notifier).fetchPersonas();

      final state = container.read(personaProvider);
      expect(state.personas.length, 2);
      expect(state.personas[0].name, 'Alice');
      expect(state.personas[1].name, 'Bob');
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    test('fetchPersonas() handles empty list', () async {
      when(() => mockClient.getPersonas()).thenAnswer(
        (_) async => _mockResponse({'personas': []}),
      );

      await container.read(personaProvider.notifier).fetchPersonas();

      final state = container.read(personaProvider);
      expect(state.personas, isEmpty);
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    // ── selectPersona ──

    test('selectPersona(persona) sets selected', () async {
      final persona = createMockPersona(id: '5', name: 'Eve');

      container.read(personaProvider.notifier).selectPersona(persona);

      final state = container.read(personaProvider);
      expect(state.selected, isNotNull);
      expect(state.selected!.id, '5');
      expect(state.selected!.name, 'Eve');
    });

    test('selectPersona replaces previous selection', () async {
      final personaA = createMockPersona(id: 'a', name: 'First');
      final personaB = createMockPersona(id: 'b', name: 'Second');

      final notifier = container.read(personaProvider.notifier);
      notifier.selectPersona(personaA);
      expect(container.read(personaProvider).selected!.name, 'First');

      notifier.selectPersona(personaB);
      expect(container.read(personaProvider).selected!.name, 'Second');
    });

    // ── fetchDetail ──

    test('fetchDetail(id) loads single persona detail', () async {
      when(() => mockClient.getPersonaDetail('42')).thenAnswer(
        (_) async => _mockResponse({
          'id': '42',
          'name': 'Dr. Detail',
          'role': 'mentor',
          'language_style': {'tone': 'formal', 'traits': ['precise']},
          'teaching_style': {
            'approach': 'socratic',
            'strictness': 0.9,
            'correction_frequency': 'every_time',
          },
          'is_preset': false,
        }),
      );

      await container.read(personaProvider.notifier).fetchDetail('42');

      final state = container.read(personaProvider);
      expect(state.selected, isNotNull);
      expect(state.selected!.id, '42');
      expect(state.selected!.name, 'Dr. Detail');
      expect(state.selected!.role, 'mentor');
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    test('fetchDetail() handles API error gracefully', () async {
      when(() => mockClient.getPersonaDetail('bad-id')).thenThrow(
        DioException(requestOptions: RequestOptions()),
      );

      await container.read(personaProvider.notifier).fetchDetail('bad-id');

      final state = container.read(personaProvider);
      expect(state.isLoading, false);
      expect(state.error, isNotNull);
      expect(state.error, contains('加载角色详情失败'));
    });

    // ── fetchPersonas error handling ──

    test('fetchPersonas() handles API error gracefully', () async {
      when(() => mockClient.getPersonas()).thenThrow(
        DioException(requestOptions: RequestOptions()),
      );

      await container.read(personaProvider.notifier).fetchPersonas();

      final state = container.read(personaProvider);
      expect(state.isLoading, false);
      expect(state.error, isNotNull);
      expect(state.error, contains('加载角色列表失败'));
      expect(state.personas, isEmpty);
    });
  });
}
