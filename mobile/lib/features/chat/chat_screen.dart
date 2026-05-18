import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../models/message.dart';
import '../../models/persona.dart';
import '../../providers/chat_provider.dart';
import '../../providers/persona_provider.dart';
import '../../shared/constants/ui_strings.dart';
import '../../shared/widgets/mellow_logo.dart';
import '../../shared/widgets/message_bubble.dart';
import '../../shared/vignettes/particle_swipe/swipe_item.dart';
import '../../shared/vignettes/pulsing_button/pulsing_button.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _showScrollToBottom = false;
  List<String> _quickPhrases = [];

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    // 加载历史消息
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final persona = ref.read(personaProvider).selected;
      if (persona != null) {
        ref.read(chatProvider.notifier).loadHistory(persona.id);
      }
    });
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // ── Scroll ──

  void _onScroll() {
    final ctrl = _scrollController;
    if (!ctrl.hasClients) return;
    final atBottom =
        ctrl.position.pixels >= ctrl.position.maxScrollExtent - 100;
    if (_showScrollToBottom == atBottom) {
      setState(() => _showScrollToBottom = !atBottom);
    }

    // 滚动到顶部时加载更多历史消息
    final chatState = ref.read(chatProvider);
    if (ctrl.position.pixels <= 50 && !chatState.isLoadingHistory) {
      final persona = ref.read(personaProvider).selected;
      if (persona != null) {
        ref.read(chatProvider.notifier).loadMoreHistory(persona.id);
      }
    }
  }

  void _scrollToBottom() {
    final ctrl = _scrollController;
    if (!ctrl.hasClients) return;
    ctrl.animateTo(
      ctrl.position.maxScrollExtent,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );
  }

  // ── Phrases ──

  Future<void> _loadPhrases() async {
    final persona = ref.read(personaProvider).selected;
    if (persona == null) return;
    final phrases =
        await ref.read(chatProvider.notifier).fetchPhrases(persona.id);
    if (!mounted) return;
    setState(() => _quickPhrases = phrases);
  }

  // ── Send ──

  void _sendMessage() {
    final text = _textController.text.trim();
    if (text.isEmpty) return;
    final persona = ref.read(personaProvider).selected;
    if (persona == null) return;
    ref.read(chatProvider.notifier).sendMessage(
          personaId: persona.id,
          content: text,
        );
    _textController.clear();
    setState(() {});
  }

  void _onQuickPhraseTap(String phrase) {
    _textController.text = phrase;
    _sendMessage();
  }

  // ── Message Interactions ──

  void _showMessageActions(Message message) {
    final persona = ref.read(personaProvider).selected;
    if (persona == null) return;

    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.copy),
              title: const Text(MellowStrings.copyText),
              onTap: () {
                Clipboard.setData(ClipboardData(text: message.content));
                if (ctx.mounted) Navigator.pop(ctx);
              },
            ),
            ListTile(
              leading: Icon(
                message.isFavorite ? Icons.star_border : Icons.star,
                color: MellowColors.favoriteGold,
              ),
              title: Text(message.isFavorite ? MellowStrings.unfavorite : MellowStrings.favorite),
              onTap: () {
                ref.read(chatProvider.notifier).toggleFavorite(message.id, persona.id);
                if (ctx.mounted) Navigator.pop(ctx);
              },
            ),
            ListTile(
              leading: const Icon(Icons.delete, color: MellowColors.error),
              title: const Text(MellowStrings.delete,
                  style: TextStyle(color: MellowColors.error)),
              onTap: () {
                ref.read(chatProvider.notifier).deleteMessage(message.id, persona.id);
                if (ctx.mounted) Navigator.pop(ctx);
              },
            ),
          ],
        ),
      ),
    );
  }

  // ── Build ──

  @override
  Widget build(BuildContext context) {
    final personaState = ref.watch(personaProvider);
    final chatState = ref.watch(chatProvider);
    final persona = personaState.selected;
    final cs = ShadTheme.of(context).colorScheme;

    // ── React to persona change → reload phrases ──
    ref.listen(personaProvider, (prev, next) {
      if (next.selected?.id != prev?.selected?.id) {
        _quickPhrases = [];
        WidgetsBinding.instance.addPostFrameCallback((_) => _loadPhrases());
      }
    });

    // ── Auto-scroll on new messages / streaming ──
    ref.listen(chatProvider, (prev, next) {
      if (next.messages.length > (prev?.messages.length ?? 0) ||
          next.isStreaming) {
        WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
      }
    });

    // ── No persona selected ──
    if (persona == null) {
      return Scaffold(
        appBar: AppBar(title: const Text(MellowStrings.appName)),
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const MellowLogo(size: 80),
              const SizedBox(height: MellowSpacing.lg),
              Text(
                MellowStrings.selectPersona,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: MellowSpacing.lg),
              FilledButton(
                onPressed: () => context.go('/personas'),
                child: const Text(MellowStrings.selectPersonaBtn),
              ),
            ],
          ),
        ),
      );
    }

    final messages = chatState.messages;
    final hasText = _textController.text.trim().isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (persona.roleEmoji case final emoji?)
              Text('$emoji ', style: const TextStyle(fontSize: 20)),
            Flexible(child: Text(persona.name)),
          ],
        ),
        actions: [
          PopupMenuButton<Persona>(
            icon: const Icon(Icons.swap_horiz),
            tooltip: MellowStrings.switchPersona,
            onSelected: (p) {
              ref.read(personaProvider.notifier).selectPersona(p);
            },
            itemBuilder: (ctx) => personaState.personas.map((p) {
              final isSelected = p.id == persona.id;
              return PopupMenuItem<Persona>(
                value: p,
                child: Row(
                  children: [
                    if (p.roleEmoji case final emoji?) Text('$emoji '),
                    Text(p.name),
                    if (isSelected) ...[
                      const SizedBox(width: MellowSpacing.sm),
                      const Icon(Icons.check,
                          size: 16, color: MellowColors.brandGreen),
                    ],
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
      body: Column(
        children: [
          // ── Error banner ──
          if (chatState.error case final error?)
            MaterialBanner(
              content: Text(error),
              actions: [
                TextButton(
                  onPressed: () =>
                      ref.read(chatProvider.notifier).clearError(),
                  child: const Text(MellowStrings.close),
                ),
              ],
            ),

          // ── Messages or empty state ──
          Expanded(
            child: chatState.isLoading && messages.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : messages.isEmpty
                ? _buildEmptyState(persona)
                : Stack(
                    children: [
                      ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.only(
                          top: MellowSpacing.sm,
                          bottom: MellowSpacing.md,
                        ),
                        itemCount: messages.length,
                        itemBuilder: (context, index) =>
                            _buildMessageItem(messages[index]),
                      ),
                      // ── Scroll-to-bottom FAB ──
                      if (_showScrollToBottom)
                        Positioned(
                          bottom: MellowSpacing.sm,
                          right: MellowSpacing.md,
                          child: FloatingActionButton.small(
                            onPressed: _scrollToBottom,
                            backgroundColor: MellowColors.brandGreen,
                            child: const Icon(Icons.keyboard_arrow_down,
                                color: Colors.white),
                          ),
                        ),
                    ],
                  ),
          ),

          // ── Bottom input bar ──
          _buildInputBar(hasText, cs),
        ],
      ),
    );
  }

  // ── Empty State ──

  Widget _buildEmptyState(Persona persona) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(MellowSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const MellowLogo(size: 80),
            const SizedBox(height: MellowSpacing.lg),
            Text(
              MellowStrings.chatWith(persona.name),
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: MellowSpacing.xl),
            if (_quickPhrases.isNotEmpty)
              Wrap(
                spacing: MellowSpacing.sm,
                runSpacing: MellowSpacing.sm,
                children: _quickPhrases.map((phrase) {
                  return ActionChip(
                    label: Text(phrase),
                    onPressed: () => _onQuickPhraseTap(phrase),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  // ── Message Item with Swipe + Long Press ──

  Widget _buildMessageItem(Message message) {
    final notifier = ref.read(chatProvider.notifier);
    final persona = ref.read(personaProvider).selected;

    return SwipeItem(
      isFavorite: message.isFavorite,
      onSwipe: (key, {required action}) {
        if (persona == null) return;
        if (action == SwipeAction.remove) {
          notifier.deleteMessage(message.id, persona.id);
        } else if (action == SwipeAction.favorite) {
          notifier.toggleFavorite(message.id, persona.id);
        }
      },
      child: GestureDetector(
        onLongPress: () => _showMessageActions(message),
        child: MessageBubble(message: message),
      ),
    );
  }

  // ── Input Bar ──

  Widget _buildInputBar(bool hasText, ShadColorScheme cs) {
    return Container(
      decoration: BoxDecoration(
        color: cs.background,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(10),
            blurRadius: 4,
            offset: const Offset(0, -1),
          ),
        ],
      ),
      padding: const EdgeInsets.fromLTRB(
        MellowSpacing.md,
        MellowSpacing.sm,
        MellowSpacing.sm,
        MellowSpacing.sm,
      ),
      child: SafeArea(
        child: Row(
          children: [
            PulsingButton(
              icon: Icons.mic,
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Voice recording coming soon')),
                );
              },
              color: MellowColors.brandOrange,
              size: 40,
            ),
            const SizedBox(width: MellowSpacing.sm),
            Expanded(
              child: TextField(
                controller: _textController,
                onChanged: (_) => setState(() {}),
                onSubmitted: (_) => _sendMessage(),
                textInputAction: TextInputAction.send,
                minLines: 1,
                maxLines: 4,
                decoration: InputDecoration(
                  hintText: MellowStrings.inputHint,
                  filled: true,
                  fillColor: cs.muted,
                  border: OutlineInputBorder(
                    borderRadius:
                        BorderRadius.circular(MellowSpacing.radiusFull),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: MellowSpacing.md,
                    vertical: MellowSpacing.sm + 2,
                  ),
                ),
              ),
            ),
            const SizedBox(width: MellowSpacing.sm),
            InkWell(
              onTap: hasText ? _sendMessage : null,
              borderRadius: BorderRadius.circular(24),
              child: Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: hasText
                      ? MellowColors.brandGreen
                      : Theme.of(context).disabledColor,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.send_rounded,
                  color: Colors.white,
                  size: 20,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
