import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:just_audio/just_audio.dart';

import '../../providers/auth_provider.dart';
import '../../providers/persona_provider.dart';
import '../../shared/constants/ui_strings.dart';
import '../../shared/constants/error_messages.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';

class PersonaDetailScreen extends ConsumerStatefulWidget {
  final String personaId;

  const PersonaDetailScreen({super.key, required this.personaId});

  @override
  ConsumerState<PersonaDetailScreen> createState() =>
      _PersonaDetailScreenState();
}

class _PersonaDetailScreenState extends ConsumerState<PersonaDetailScreen> {
  final _audioPlayer = AudioPlayer();
  bool _isPlayingVoice = false;

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(personaProvider.notifier).fetchDetail(widget.personaId);
    });
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _tryVoice() async {
    setState(() => _isPlayingVoice = true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.getPersonaVoice(widget.personaId);
      if (!mounted) return;
      final bytes = res.data;
      if (bytes is List<int>) {
        await _audioPlayer.setAudioSource(
          AudioSource.uri(
            Uri.dataFromBytes(bytes, mimeType: 'audio/mpeg'),
          ),
        );
        if (!mounted) return;
        await _audioPlayer.play();
        if (!mounted) return;
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text(MellowErrors.voicePlayFailed)),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isPlayingVoice = false);
      }
    }
  }

  void _startChat() {
    final personaState = ref.read(personaProvider);
    if (personaState.selected case final persona?) {
      ref.read(personaProvider.notifier).selectPersona(persona);
    }
    context.go('/chat');
  }

  @override
  Widget build(BuildContext context) {
    final personaState = ref.watch(personaProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          personaState.selected?.name ?? MellowStrings.personaDetail,
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      body: SafeArea(
        child: Builder(
        builder: (context) {
          // 加载中
          if (personaState.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          // 错误
          final detailError = personaState.error;
          if (detailError != null && personaState.selected == null) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.error_outline,
                      size: 48, color: MellowColors.error),
                  const SizedBox(height: MellowSpacing.md),
                  Text(detailError,
                      style: TextStyle(color: MellowColors.error)),
                  const SizedBox(height: MellowSpacing.md),
                  TextButton(
                    onPressed: () {
                      ref
                          .read(personaProvider.notifier)
                          .fetchDetail(widget.personaId);
                    },
                    child: const Text(MellowStrings.retry),
                  ),
                ],
              ),
            );
          }

          final persona = personaState.selected;
          if (persona == null) {
            return const Center(child: Text(MellowStrings.personaUnavailable));
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(MellowSpacing.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 角色表情
                Center(
                  child: Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      color: MellowColors.brandGreen.withAlpha(25),
                      borderRadius:
                          BorderRadius.circular(MellowSpacing.radiusXl),
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      persona.roleEmoji ?? '🤖',
                      style: const TextStyle(fontSize: 48),
                    ),
                  ),
                ),
                const SizedBox(height: MellowSpacing.md),

                // 名称 + 角色
                Text(
                  persona.name,
                  textAlign: TextAlign.center,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: MellowSpacing.xs),
                Text(
                  persona.role,
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodyLarge?.copyWith(
                    color: MellowColors.textSecondary(context),
                  ),
                ),
                const SizedBox(height: MellowSpacing.xl),

                // 语言风格
                PersonaInfoSection(
                  title: MellowStrings.languageStyle,
                  icon: Icons.translate,
                  children: [
                    PersonaInfoRow(
                        label: MellowStrings.tone, value: persona.languageStyle.tone),
                    if (persona.languageStyle.traits.isNotEmpty)
                      PersonaInfoRow(
                        label: MellowStrings.traits,
                        value: persona.languageStyle.traits.join('、'),
                      ),
                  ],
                ),
                const SizedBox(height: MellowSpacing.md),

                // 教学风格
                PersonaInfoSection(
                  title: MellowStrings.teachingStyle,
                  icon: Icons.school,
                  children: [
                    PersonaInfoRow(
                        label: MellowStrings.approach,
                        value: persona.teachingStyle.approach),
                    PersonaInfoRow(
                      label: MellowStrings.strictness,
                      value:
                          '${(persona.teachingStyle.strictness * 100).toInt()}%',
                    ),
                    PersonaInfoRow(
                      label: MellowStrings.correctionFreq,
                      value: persona.teachingStyle.correctionFrequency,
                    ),
                  ],
                ),
                const SizedBox(height: MellowSpacing.xl),

                // 试听语音按钮
                SizedBox(
                  height: 48,
                  child: OutlinedButton.icon(
                    onPressed: _isPlayingVoice ? null : _tryVoice,
                    icon: _isPlayingVoice
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child:
                                CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.volume_up),
                    label:
                        Text(_isPlayingVoice ? MellowStrings.playing : MellowStrings.tryVoice),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: MellowColors.brandGreen,
                      side: const BorderSide(
                          color: MellowColors.brandGreen),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(
                            MellowSpacing.radiusMd),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: MellowSpacing.md),

                // 开始聊天按钮
                SizedBox(
                  height: 48,
                  child: ElevatedButton.icon(
                    onPressed: _startChat,
                    icon: const Icon(Icons.chat_bubble_outline),
                    label: const Text(
                      MellowStrings.startChat,
                      style: TextStyle(
                          fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: MellowColors.brandGreen,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(
                            MellowSpacing.radiusMd),
                      ),
                      elevation: 0,
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
      ),
    );
  }
}

/// 信息区块
@visibleForTesting
class PersonaInfoSection extends StatelessWidget {
  final String title;
  final IconData icon;
  final List<Widget> children;

  const PersonaInfoSection({
    super.key,
    required this.title,
    required this.icon,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(MellowSpacing.md),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(MellowSpacing.radiusLg),
        border: Border.all(
          color: MellowColors.border(context).withAlpha(128),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 18, color: MellowColors.brandGreen),
              const SizedBox(width: MellowSpacing.sm),
              Text(
                title,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: MellowColors.brandGreen,
                ),
              ),
            ],
          ),
          const SizedBox(height: MellowSpacing.sm),
          ...children,
        ],
      ),
    );
  }
}

/// 信息行
@visibleForTesting
class PersonaInfoRow extends StatelessWidget {
  final String label;
  final String value;

  const PersonaInfoRow({super.key, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.only(bottom: MellowSpacing.xs),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 64,
            child: Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: MellowColors.textSecondary(context),
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: theme.textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}
