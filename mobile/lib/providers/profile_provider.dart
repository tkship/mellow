import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/learning_stats.dart';
import '../services/api_client.dart';
import '../shared/constants/error_messages.dart';
import 'auth_provider.dart';

class ProfileState {
  final ProfileInfo? info;
  final bool isLoading;
  final String? error;

  const ProfileState({this.info, this.isLoading = false, this.error});

  ProfileState copyWith({
    ProfileInfo? info,
    bool? isLoading,
    String? error,
  }) =>
      ProfileState(
        info: info ?? this.info,
        isLoading: isLoading ?? this.isLoading,
        error: error,
      );
}

class ProfileNotifier extends Notifier<ProfileState> {
  @override
  ProfileState build() => const ProfileState();

  Future<void> fetchProfile() async {
    state = state.copyWith(isLoading: true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getProfile();
      final info = ProfileInfo.fromJson(res.data as Map<String, dynamic>);
      state = state.copyWith(info: info, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: MellowErrors.loadFailed);
    }
  }

  Future<void> updateProfile(String cefrLevel) async {
    try {
      final client = ref.read(apiClientProvider);
      await client.updateProfile({'cefr_level': cefrLevel});
      await fetchProfile();
    } catch (_) {
      state = state.copyWith(error: MellowErrors.updateProfileFailed);
    }
  }
}

final profileProvider = NotifierProvider<ProfileNotifier, ProfileState>(
  ProfileNotifier.new,
);
