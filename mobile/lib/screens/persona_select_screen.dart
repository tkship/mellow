import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';

import '../providers/persona_provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/persona_card.dart';
import 'chat_screen.dart';
import 'login_screen.dart';

class PersonaSelectScreen extends StatefulWidget {
  const PersonaSelectScreen({super.key});

  @override
  State<PersonaSelectScreen> createState() => _PersonaSelectScreenState();
}

class _PersonaSelectScreenState extends State<PersonaSelectScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<PersonaProvider>().loadPresets());
  }

  void _navigateToChat() {
    Navigator.of(context).pushAndRemoveUntil(
      PageRouteBuilder(
        pageBuilder: (_, __, ___) => const ChatScreen(),
        transitionsBuilder: (_, animation, __, child) => FadeTransition(
          opacity: animation,
          child: child,
        ),
        transitionDuration: const Duration(milliseconds: 400),
      ),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final personaProvider = context.watch<PersonaProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        title: Text(
          '选择你的学习伙伴',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.onSurface,
          ),
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 4),
            decoration: BoxDecoration(
              color: theme.colorScheme.errorContainer.withOpacity(0.5),
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: Icon(Icons.logout, color: theme.colorScheme.error, size: 20),
              onPressed: () async {
                await context.read<AuthProvider>().logout();
                if (context.mounted) {
                  Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                    (_) => false,
                  );
                }
              },
            ),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Background gradient
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    theme.colorScheme.primaryContainer.withOpacity(0.35),
                    theme.colorScheme.surface,
                    theme.colorScheme.secondaryContainer.withOpacity(0.10),
                  ],
                  stops: const [0.0, 0.45, 1.0],
                ),
              ),
            ),
          ),
          // Decorative floating circles (background)
          ..._buildDecorativeCircles(theme),
          // Main content
          SafeArea(
            child: personaProvider.presets.isEmpty
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 64,
                          height: 64,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                theme.colorScheme.primaryContainer,
                                theme.colorScheme.secondaryContainer,
                              ],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: theme.colorScheme.primary.withOpacity(0.3),
                                blurRadius: 20,
                                offset: const Offset(0, 8),
                              ),
                            ],
                          ),
                          child: Icon(Icons.people,
                              size: 30, color: theme.colorScheme.primary),
                        ).animate(onPlay: (ctrl) => ctrl.repeat(reverse: true))
                          .scale(
                            begin: const Offset(0.92, 0.92),
                            end: const Offset(1.06, 1.06),
                            duration: 1500.ms,
                            curve: Curves.easeInOut,
                          ),
                        const SizedBox(height: 20),
                        CircularProgressIndicator(
                          color: theme.colorScheme.primary,
                          strokeWidth: 2.5,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          '正在准备学习伙伴...',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.outline,
                          ),
                        ),
                      ],
                    ),
                  )
                : Column(
                    children: [
                      // Header section
                      Padding(
                        padding: const EdgeInsets.fromLTRB(20, 8, 20, 0),
                        child: Row(
                          children: [
                            Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  colors: [
                                    theme.colorScheme.primary,
                                    theme.colorScheme.tertiary,
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(14),
                                boxShadow: [
                                  BoxShadow(
                                    color: theme.colorScheme.primary.withOpacity(0.3),
                                    blurRadius: 12,
                                    offset: const Offset(0, 4),
                                  ),
                                ],
                              ),
                              child: const Icon(Icons.auto_awesome,
                                  color: Colors.white, size: 20),
                            ).animate().fadeIn(delay: 100.ms).scale(
                                  begin: const Offset(0, 0),
                                  curve: Curves.elasticOut,
                                ),
                            const SizedBox(width: 12),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  '发现你的 AI 学习伙伴',
                                  style: theme.textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.w700,
                                    color: theme.colorScheme.onSurface,
                                  ),
                                ).animate().fadeIn(delay: 200.ms).slideY(begin: 4),
                                const SizedBox(height: 2),
                                Text(
                                  '每位伙伴都有独特的教学风格',
                                  style: theme.textTheme.bodySmall?.copyWith(
                                    color: theme.colorScheme.outline,
                                  ),
                                ).animate().fadeIn(delay: 300.ms).slideY(begin: 4),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      // Card list
                      Expanded(
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 4),
                          itemCount: personaProvider.presets.length,
                          itemBuilder: (_, i) {
                            final persona = personaProvider.presets[i];
                            return PersonaCard(
                              persona: persona,
                              onTap: () {
                                personaProvider.selectPersona(persona);
                                _navigateToChat();
                              },
                            ).animate()
                              .fadeIn(delay: (200 + i * 100).ms, duration: 500.ms)
                              .slideY(begin: 0.2, delay: (200 + i * 100).ms, duration: 500.ms, curve: Curves.easeOutCubic)
                              .scale(
                                begin: const Offset(0.95, 0.95),
                                delay: (200 + i * 100).ms,
                                duration: 500.ms,
                                curve: Curves.easeOutCubic,
                              );
                          },
                        ),
                      ),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  List<Widget> _buildDecorativeCircles(ThemeData theme) {
    return [
      // Top-right large circle
      Positioned(
        top: -60,
        right: -40,
        child: IgnorePointer(
          child: Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  theme.colorScheme.primary.withOpacity(0.10),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
      ),
      // Bottom-left accent
      Positioned(
        bottom: -40,
        left: -30,
        child: IgnorePointer(
          child: Container(
            width: 160,
            height: 160,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  theme.colorScheme.secondary.withOpacity(0.08),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
      ),
      // Center faint glow
      Positioned(
        top: MediaQuery.of(context).size.height * 0.35,
        right: -30,
        child: IgnorePointer(
          child: Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  theme.colorScheme.tertiary.withOpacity(0.06),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
      ),
    ];
  }
}
