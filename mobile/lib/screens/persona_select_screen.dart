import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/persona_provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/persona_card.dart';
import 'chat_screen.dart';

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

  @override
  Widget build(BuildContext context) {
    final personaProvider = context.watch<PersonaProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('选择你的学习伙伴'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthProvider>().logout(),
          ),
        ],
      ),
      body: personaProvider.presets.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: personaProvider.presets.length,
              itemBuilder: (_, i) {
                final persona = personaProvider.presets[i];
                return PersonaCard(
                  persona: persona,
                  onTap: () {
                    personaProvider.selectPersona(persona);
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(builder: (_) => const ChatScreen()),
                    );
                  },
                );
              },
            ),
    );
  }
}
