import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';

import '../models/persona.dart';
import '../providers/auth_provider.dart';
import '../providers/persona_provider.dart';
import '../widgets/persona_card.dart';
import 'chat_screen.dart';
import 'login_screen.dart';

class PersonaSelectScreen extends StatefulWidget {
  const PersonaSelectScreen({super.key});
  @override
  State<PersonaSelectScreen> createState() => _PersonaSelectScreenState();
}

class _PersonaSelectScreenState extends State<PersonaSelectScreen> {
  Persona? _sel;

  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<PersonaProvider>().loadPresets());
  }

  void _confirm() {
    if (_sel == null) return;
    context.read<PersonaProvider>().selectPersona(_sel!);
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const ChatScreen()),
      (_) => false,
    );
  }

  Future<void> _logout() async {
    await context.read<AuthProvider>().logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final presets = context.watch<PersonaProvider>().presets;

    return Scaffold(
      body: SafeArea(
        child: presets.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : Column(
                children: [
                  // Header
                  Padding(
                    padding: const EdgeInsets.fromLTRB(24, 20, 16, 12),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '选择学习伙伴',
                                style: theme.textTheme.headlineSmall?.copyWith(
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '今天谁陪你学英语？',
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: cs.outline,
                                ),
                              ),
                            ],
                          ),
                        ),
                        TextButton(
                          onPressed: _logout,
                          child: const Text('退出'),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  // Card carousel
                  Expanded(
                    child: ListView.builder(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      itemCount: presets.length,
                      itemBuilder: (_, i) {
                        final p = presets[i];
                        return PersonaCard(
                          persona: p,
                          selected: _sel?.id == p.id,
                          onTap: () => setState(() => _sel = p),
                        ).animate().fadeIn(
                              duration: 350.ms,
                              delay: (i * 100).ms,
                            ).slideY(
                              begin: 20,
                              duration: 350.ms,
                              curve: Curves.easeOutCubic,
                            );
                      },
                    ),
                  ),
                  // Confirm button
                  Padding(
                    padding: const EdgeInsets.all(20),
                    child: FilledButton(
                      onPressed: _sel != null ? _confirm : null,
                      child: const Text('开始聊天'),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
