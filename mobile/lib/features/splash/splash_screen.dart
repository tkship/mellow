import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../providers/auth_provider.dart';
import '../../providers/theme_provider.dart';
import '../../shared/constants/ui_strings.dart';
import '../../shared/widgets/mellow_logo.dart';
import '../../theme/colors.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _animCtrl;
  late final Animation<double> _fadeAnim;
  bool _showButton = false;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _fadeAnim = CurvedAnimation(parent: _animCtrl, curve: Curves.easeIn);
    _animCtrl.forward();
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted && ref.read(authProvider).status == AuthStatus.unknown) {
        setState(() => _showButton = true);
      }
    });
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    ref.listen<AuthState>(authProvider, (prev, next) {
      if (next.status == AuthStatus.authenticated) context.go('/chat');
      if (next.status == AuthStatus.unauthenticated) {
        setState(() => _showButton = true);
      }
    });

    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: SafeArea(
        child: Center(
          child: FadeTransition(
            opacity: _fadeAnim,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const MellowLogo(size: 96),
                const SizedBox(height: 32),
                Text('Mellow',
                    style: theme.textTheme.headlineLarge?.copyWith(
                        color: MellowColors.brandGreen,
                        fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text(MellowStrings.appSubtitle,
                    style: theme.textTheme.bodyLarge?.copyWith(
                        color: theme.colorScheme.onSurface.withAlpha(150))),
                const SizedBox(height: 64),
                if (_showButton) ...[
                  FilledButton(
                    onPressed: () => context.go('/auth/login'),
                    style: FilledButton.styleFrom(
                        backgroundColor: MellowColors.brandGreen,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 48, vertical: 16)),
                    child: const Text(MellowStrings.start,
                        style: TextStyle(fontSize: 18)),
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () =>
                        ref.read(authProvider.notifier).devLogin(),
                    child: const Text('🔧 开发模式 (跳过登录)',
                        style: TextStyle(color: MellowColors.brandOrange)),
                  ),
                ] else
                  const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(strokeWidth: 2)),
              ],
            ),
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.small(
        onPressed: () => ref.read(themeProvider.notifier).toggle(),
        child: Icon(Theme.of(context).brightness == Brightness.dark
            ? Icons.light_mode
            : Icons.dark_mode),
      ),
    );
  }
}
