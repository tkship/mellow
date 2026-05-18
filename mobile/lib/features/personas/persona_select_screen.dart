import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../models/persona.dart';
import '../../providers/persona_provider.dart';
import '../../shared/constants/ui_strings.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';

class PersonaSelectScreen extends ConsumerStatefulWidget {
  const PersonaSelectScreen({super.key});

  @override
  ConsumerState<PersonaSelectScreen> createState() =>
      _PersonaSelectScreenState();
}

class _PersonaSelectScreenState extends ConsumerState<PersonaSelectScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(personaProvider.notifier).fetchPersonas();
    });
  }

  @override
  Widget build(BuildContext context) {
    final personaState = ref.watch(personaProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          MellowStrings.chooseTeacher,
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => context.go('/chat'),
            style: TextButton.styleFrom(
              foregroundColor: MellowColors.textSecondary(context),
            ),
            child: const Text(MellowStrings.skip),
          ),
        ],
      ),
      body: SafeArea(
        child: Builder(
        builder: (context) {
          // 加载中 — 骨架屏
          if (personaState.isLoading && personaState.personas.isEmpty) {
            return ListView.builder(
              padding: const EdgeInsets.all(MellowSpacing.md),
              itemCount: 4,
              itemBuilder: (context, index) => const PersonaShimmerCard(),
            );
          }

          // 错误状态
          final selectError = personaState.error;
          if (selectError != null && personaState.personas.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.error_outline,
                      size: 48, color: MellowColors.error),
                  const SizedBox(height: MellowSpacing.md),
                  Text(
                    selectError,
                    style: TextStyle(color: MellowColors.error),
                  ),
                  const SizedBox(height: MellowSpacing.md),
                  TextButton(
                    onPressed: () {
                      ref.read(personaProvider.notifier).fetchPersonas();
                    },
                    child: const Text(MellowStrings.retry),
                  ),
                ],
              ),
            );
          }

          // 空状态
          if (personaState.personas.isEmpty) {
            return const Center(
              child: Text(MellowStrings.noPersonas),
            );
          }

          // 角色列表
          // TODO: Replace with parallax_travel_cards_list
          return ListView.builder(
            padding: const EdgeInsets.all(MellowSpacing.md),
            itemCount: personaState.personas.length,
            itemBuilder: (context, index) {
              final persona = personaState.personas[index];
              return Padding(
                padding: const EdgeInsets.only(bottom: MellowSpacing.md),
                child: PersonaListCard(
                  persona: persona,
                  onTap: () {
                    ref
                        .read(personaProvider.notifier)
                        .selectPersona(persona);
                    context.go('/personas/${persona.id}');
                  },
                ),
              );
            },
          );
        },
      ),
      ),
    );
  }
}

/// 角色卡片
@visibleForTesting
class PersonaListCard extends StatelessWidget {
  final Persona persona;
  final VoidCallback onTap;

  const PersonaListCard({super.key, required this.persona, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final emoji = persona.roleEmoji ?? '🤖';
    final name = persona.name;
    final role = persona.role;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(MellowSpacing.radiusLg),
        side: BorderSide(color: MellowColors.border(context).withAlpha(128)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(MellowSpacing.radiusLg),
        child: Padding(
          padding: const EdgeInsets.all(MellowSpacing.md),
          child: Row(
            children: [
              // 角色表情
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: MellowColors.brandGreen.withAlpha(25),
                  borderRadius:
                      BorderRadius.circular(MellowSpacing.radiusMd),
                ),
                alignment: Alignment.center,
                child: Text(
                  emoji,
                  style: const TextStyle(fontSize: 28),
                ),
              ),
              const SizedBox(width: MellowSpacing.md),

              // 角色信息
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: MellowSpacing.xs),
                    Text(
                      role,
                      style: theme.textTheme.bodySmall?.copyWith(
          color: MellowColors.textSecondary(context),
                      ),
                    ),
                  ],
                ),
              ),

              // 箭头
              Icon(
                Icons.chevron_right,
                color: MellowColors.textSecondary(context),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 骨架屏占位卡片
@visibleForTesting
class PersonaShimmerCard extends StatelessWidget {
  const PersonaShimmerCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(MellowSpacing.radiusLg),
        side: BorderSide(color: MellowColors.border(context).withAlpha(128)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(MellowSpacing.md),
        child: Row(
          children: [
            // 头像占位
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: MellowColors.border(context).withAlpha(80),
                borderRadius: BorderRadius.circular(MellowSpacing.radiusMd),
              ),
            ),
            const SizedBox(width: MellowSpacing.md),
            // 文字占位
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    height: 16,
                    width: 120,
                    decoration: BoxDecoration(
                      color: MellowColors.border(context).withAlpha(80),
                      borderRadius:
                          BorderRadius.circular(MellowSpacing.radiusSm),
                    ),
                  ),
                  const SizedBox(height: MellowSpacing.sm),
                  Container(
                    height: 12,
                    width: 180,
                    decoration: BoxDecoration(
                      color: MellowColors.border(context).withAlpha(80),
                      borderRadius:
                          BorderRadius.circular(MellowSpacing.radiusSm),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
