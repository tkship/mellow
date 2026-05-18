import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../providers/auth_provider.dart';
import '../../providers/learn_provider.dart';
import '../../providers/persona_provider.dart';
import '../../providers/profile_provider.dart';
import '../../providers/theme_provider.dart';
import '../../shared/constants/ui_strings.dart';
import '../../shared/widgets/mellow_logo.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(profileProvider.notifier).fetchProfile();
      ref.read(learnProvider.notifier).fetchStats();
    });
  }

  Future<void> _handleLogout() async {
    final router = GoRouter.of(context);
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text(MellowStrings.logoutTitle),
        content: const Text(MellowStrings.logoutConfirm),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text(MellowStrings.cancel),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: MellowColors.error),
            child: const Text(MellowStrings.logoutAction),
          ),
        ],
      ),
    );
    if (!mounted) return;
    if (confirmed == true) {
      await ref.read(authProvider.notifier).logout();
      if (!mounted) return;
      router.go('/splash');
    }
  }

  Future<void> _showCefrDialog() async {
    final messenger = ScaffoldMessenger.of(context);
    const levels = ['A0', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    final current =
        ref.read(profileProvider).info?.cefrLevel ?? 'A0';

    final selected = await showDialog<String>(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text(MellowStrings.selectGoal),
        children: levels.map((level) {
          final isSelected = level == current;
          return SimpleDialogOption(
            onPressed: () => Navigator.pop(ctx, level),
            child: Row(
              children: [
                Text(level,
                    style: TextStyle(
                      fontWeight:
                          isSelected ? FontWeight.bold : FontWeight.normal,
                      color: isSelected ? MellowColors.brandGreen : null,
                    )),
                if (isSelected) ...[
                  const Spacer(),
                  const Icon(Icons.check,
                      color: MellowColors.brandGreen, size: 20),
                ],
              ],
            ),
          );
        }).toList(),
      ),
    );

    if (!mounted) return;
    if (selected != null) {
      await ref.read(profileProvider.notifier).updateProfile(selected);
      if (!mounted) return;
      final error = ref.read(profileProvider).error;
      if (error != null) {
        messenger.showSnackBar(
          SnackBar(content: Text(error)),
        );
      } else {
        messenger.showSnackBar(
          const SnackBar(content: Text('学习目标已更新')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final profileState = ref.watch(profileProvider);
    final learnState = ref.watch(learnProvider);
    final stats = learnState.stats;
    final personaState = ref.watch(personaProvider);
    final themeMode = ref.watch(themeProvider);
    final theme = Theme.of(context);
    final user = authState.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text(MellowStrings.myProfile),
        centerTitle: false,
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(MellowSpacing.md),
          children: [
          // 资料加载错误
          if (profileState.error case final error?)
            MaterialBanner(
              content: Text(error),
              actions: [
                TextButton(
                  onPressed: () =>
                      ref.read(profileProvider.notifier).fetchProfile(),
                  child: const Text(MellowStrings.retry),
                ),
              ],
            ),
          // 用户头像区
          Center(
            child: Column(
              children: [
                const MellowLogo(size: 64),
                const SizedBox(height: MellowSpacing.sm),
                Text(
                  user?.username ?? MellowStrings.defaultUser,
                  style: theme.textTheme.titleLarge,
                ),
                const SizedBox(height: 4),
                Text(
                  MellowStrings.learnerLevel(profileState.info?.cefrLevel ?? 'A0'),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withAlpha(150),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: MellowSpacing.lg),

          // 统计行
          if (learnState.isLoading && stats == null)
            const Center(child: CircularProgressIndicator())
          else
            Row(
              children: [
                _StatCard(
                    label: MellowStrings.messageCount, value: '${stats?.totalMessages ?? 0}'),
                const SizedBox(width: MellowSpacing.sm),
                _StatCard(
                    label: MellowStrings.learningDays, value: '${stats?.learningDays ?? 0}'),
                const SizedBox(width: MellowSpacing.sm),
                _StatCard(
                    label: MellowStrings.checkinCount, value: '${stats?.checkInCount ?? 0}'),
              ],
            ),
          const SizedBox(height: MellowSpacing.lg),

          // 当前角色卡
          if (personaState.selected case final persona?)
            Card(
              child: ListTile(
                leading: Text(persona.roleEmoji ?? '🤖',
                    style: const TextStyle(fontSize: 28)),
                title: Text(persona.name),
                subtitle: Text(persona.role),
                trailing: const Icon(Icons.swap_horiz),
                onTap: () => context.go('/personas'),
              ),
            ),
          const SizedBox(height: MellowSpacing.md),

          // 设置列表
          _SettingItem(
            icon: Icons.swap_horiz,
            title: MellowStrings.switchRole,
            onTap: () => context.go('/personas'),
          ),
          _SettingItem(
            icon: Icons.record_voice_over,
            title: MellowStrings.voiceSettings,
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text(MellowStrings.underDevelopment)),
              );
            },
          ),
          _SettingItem(
            icon: Icons.school,
            title: MellowStrings.learningGoal,
            subtitle: MellowStrings.currentLevel(profileState.info?.cefrLevel ?? 'A0'),
            onTap: _showCefrDialog,
          ),
          _SettingItem(
            icon: themeMode == ThemeMode.dark
                ? Icons.dark_mode
                : Icons.light_mode,
            title: MellowStrings.darkMode,
            trailing: Switch(
              value: themeMode == ThemeMode.dark,
              onChanged: (_) => ref.read(themeProvider.notifier).toggle(),
              activeThumbColor: MellowColors.brandGreen,
            ),
          ),
          const Divider(),
          _SettingItem(
            icon: Icons.logout,
            title: MellowStrings.logout,
            titleColor: MellowColors.error,
            onTap: _handleLogout,
          ),
          const SizedBox(height: MellowSpacing.xl),

          // 页脚
          Center(
            child: Text(
              MellowStrings.about,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withAlpha(100),
              ),
            ),
          ),
          const SizedBox(height: MellowSpacing.lg),
          ],
        ),
      ),
    );
  }
}

/// 统计卡片
class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  const _StatCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: MellowSpacing.md),
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          borderRadius: BorderRadius.circular(MellowSpacing.radiusMd),
          border: Border.all(color: theme.dividerColor.withAlpha(80)),
        ),
        child: Column(
          children: [
            Text(value,
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 2),
            Text(label, style: theme.textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}

/// 设置项
class _SettingItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final Color? titleColor;
  final Widget? trailing;
  final VoidCallback? onTap;

  const _SettingItem({
    required this.icon,
    required this.title,
    this.subtitle,
    this.titleColor,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListTile(
      leading: Icon(icon, color: titleColor ?? theme.iconTheme.color),
      title: Text(title,
          style: TextStyle(
              color: titleColor ?? theme.textTheme.bodyLarge?.color)),
      subtitle: subtitle != null ? Text(subtitle!) : null,
      trailing: trailing ?? (onTap != null ? const Icon(Icons.chevron_right) : null),
      onTap: onTap,
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(MellowSpacing.radiusMd)),
    );
  }
}
