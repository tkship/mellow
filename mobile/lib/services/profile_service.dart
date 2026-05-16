import 'package:dio/dio.dart';

import '../config/api_config.dart';

class ProfileService {
  final Dio _dio;

  ProfileService({String? token})
      : _dio = Dio(BaseOptions(
          baseUrl: ApiConfig.baseUrl,
          headers: token != null ? {'Authorization': 'Bearer $token'} : {},
        ));

  Future<Map<String, dynamic>> getProfile() async {
    final res = await _dio.get('${ApiConfig.apiPrefix}/profile');
    return res.data;
  }

  Future<List<dynamic>> getMistakes() async {
    final res = await _dio.get('${ApiConfig.apiPrefix}/profile/mistakes');
    return res.data['mistakes'] ?? [];
  }

  Future<List<dynamic>> getEmotions(String personaId) async {
    final res = await _dio.get(
      '${ApiConfig.apiPrefix}/memory/emotions',
      queryParameters: {'persona_id': personaId},
    );
    return res.data['emotions'] ?? [];
  }

  Future<List<dynamic>> getFacts(String personaId) async {
    final res = await _dio.get(
      '${ApiConfig.apiPrefix}/memory/facts',
      queryParameters: {'persona_id': personaId},
    );
    return res.data['facts'] ?? [];
  }

  Future<String?> getMemorySummary(String personaId) async {
    final res = await _dio.get(
      '${ApiConfig.apiPrefix}/memory/summary',
      queryParameters: {'persona_id': personaId},
    );
    return res.data['summary'] as String?;
  }
}
