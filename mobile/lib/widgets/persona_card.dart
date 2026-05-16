import 'package:flutter/material.dart';
import '../models/persona.dart';

class PersonaCard extends StatelessWidget {
  const PersonaCard({super.key, required this.persona, required this.onTap, this.selected = false});
  final Persona persona;
  final VoidCallback onTap;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final tags = [...persona.languageStyle.traits, persona.teachingStyle.approach];

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 350),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: cs.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: selected ? cs.primary : cs.outlineVariant.withAlpha(60), width: selected ? 2 : 1),
          boxShadow: selected ? [
            BoxShadow(color: cs.primary.withAlpha(35), blurRadius: 16, offset: const Offset(0, 6)),
            BoxShadow(color: cs.primary.withAlpha(15), blurRadius: 8, offset: const Offset(0, 2)),
          ] : [
            BoxShadow(color: cs.shadow.withAlpha(12), blurRadius: 8, offset: const Offset(0, 2)),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 64, height: 64,
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [cs.primary, cs.tertiary]),
                borderRadius: BorderRadius.circular(18),
              ),
              child: Center(child: Text(persona.roleEmoji, style: const TextStyle(fontSize: 32))),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(persona.name, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 2),
                  Text(persona.role, style: theme.textTheme.bodySmall?.copyWith(color: cs.outline)),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                    decoration: BoxDecoration(color: cs.tertiaryContainer, borderRadius: BorderRadius.circular(8)),
                    child: Text(persona.intimacyLevel, style: theme.textTheme.labelSmall?.copyWith(color: cs.onTertiaryContainer)),
                  ),
                  if (tags.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6, runSpacing: 4,
                      children: tags.where((t) => t.isNotEmpty).map((t) => Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(color: cs.surfaceContainerHighest, borderRadius: BorderRadius.circular(8)),
                        child: Text(t, style: theme.textTheme.labelSmall?.copyWith(color: cs.outline)),
                      )).toList(),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
