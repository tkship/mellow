import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../models/persona.dart';

class PersonaCard extends StatefulWidget {
  final Persona persona;
  final VoidCallback onTap;

  const PersonaCard({super.key, required this.persona, required this.onTap});

  @override
  State<PersonaCard> createState() => _PersonaCardState();
}

class _PersonaCardState extends State<PersonaCard>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pressCtrl;
  late final Animation<double> _pressScale;
  late final Animation<double> _pressElevation;

  @override
  void initState() {
    super.initState();
    _pressCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 150),
    );
    _pressScale = Tween<double>(begin: 1.0, end: 1.02).animate(
      CurvedAnimation(parent: _pressCtrl, curve: Curves.easeOut),
    );
    _pressElevation = Tween<double>(begin: 1.0, end: 8.0).animate(
      CurvedAnimation(parent: _pressCtrl, curve: Curves.easeOut),
    );
  }

  @override
  void dispose() {
    _pressCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return AnimatedBuilder(
      animation: _pressCtrl,
      builder: (_, child) => Transform.scale(
        scale: _pressScale.value,
        child: child,
      ),
      child: Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () {
              _pressCtrl.forward().then((_) {
                _pressCtrl.reverse();
                widget.onTap();
              });
            },
            onTapDown: (_) => _pressCtrl.forward(),
            onTapCancel: () => _pressCtrl.reverse(),
            borderRadius: BorderRadius.circular(20),
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    cs.surfaceContainerLow,
                    cs.surfaceContainerLow,
                    cs.primaryContainer.withOpacity(0.12),
                  ],
                ),
                border: Border(
                  left: BorderSide(
                    color: cs.primary.withOpacity(0.35),
                    width: 3.5,
                  ),
                ),
                boxShadow: [
                  BoxShadow(
                    color: cs.primary.withOpacity(0.06),
                    blurRadius: _pressElevation.value,
                    offset: const Offset(0, 2),
                  ),
                  BoxShadow(
                    color: cs.primary.withOpacity(0.04),
                    blurRadius: _pressElevation.value * 2,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Emoji section — larger, gradient background
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        cs.primaryContainer,
                        cs.secondaryContainer,
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: cs.primary.withOpacity(0.2),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Center(
                    child: Text(
                      widget.persona.roleEmoji,
                      style: const TextStyle(fontSize: 38),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                // Text content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Name
                      Text(
                        widget.persona.name,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                          color: cs.onSurface,
                        ),
                      ),
                      const SizedBox(height: 4),
                      // Role
                      Text(
                        widget.persona.role,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: cs.primary,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      // Tone / description
                      Text(
                        widget.persona.languageStyle.tone,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: cs.onSurfaceVariant,
                        ),
                      ),
                      // Style trait chips
                      if (widget.persona.languageStyle.traits.isNotEmpty) ...[
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 6,
                          runSpacing: 4,
                          children: widget.persona.languageStyle.traits
                              .map(
                                (trait) => Chip(
                                  label: Text(trait),
                                  labelStyle: theme.textTheme.labelSmall,
                                  backgroundColor: cs.secondaryContainer,
                                  side: BorderSide.none,
                                  padding: EdgeInsets.zero,
                                  visualDensity: VisualDensity.compact,
                                  materialTapTargetSize:
                                      MaterialTapTargetSize.shrinkWrap,
                                ),
                              )
                              .toList(),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                // CTA button
                FilledButton.tonalIcon(
                  onPressed: () {
                    _pressCtrl.forward().then((_) {
                      _pressCtrl.reverse();
                      widget.onTap();
                    });
                  },
                  icon: const Icon(Icons.arrow_forward_rounded, size: 18),
                  label: const Text('开始'),
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 8),
                    shape: const StadiumBorder(),
                  ),
                ),
              ],
            ),
          ),
        ),
        ),
      ),
    );
  }
}
