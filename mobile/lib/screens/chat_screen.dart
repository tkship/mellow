import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';

import '../models/word_entry.dart';
import '../providers/chat_provider.dart';
import '../providers/persona_provider.dart';
import '../services/api_client.dart';
import '../services/knowledge_service.dart';
import '../services/profile_service.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/typing_indicator.dart';
import '../widgets/voice_button.dart';
import 'persona_select_screen.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _text = TextEditingController();
  final _scroll = ScrollController();
  final _know = KnowledgeService(ApiClient());

  @override
  void dispose() {
    _text.dispose();
    _scroll.dispose();
    super.dispose();
  }

  void _send() {
    final t = _text.text.trim();
    if (t.isEmpty) return;
    final p = context.read<PersonaProvider>().selected;
    if (p == null) return;
    context.read<ChatProvider>().sendMessage(p.id, t);
    _text.clear();
    _scrollToBot();
  }

  void _scrollToBot() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) _scroll.animateTo(0, duration: 250.ms, curve: Curves.easeOut);
    });
  }

  void _showTopSheet(Widget child) {
    showGeneralDialog(
      context: context,
      barrierDismissible: true,
      barrierColor: Colors.black.withAlpha(100),
      barrierLabel: '',
      transitionDuration: 350.ms,
      pageBuilder: (_, __, ___) => child,
      transitionBuilder: (_, anim, __, child) => SlideTransition(
        position: Tween<Offset>(begin: const Offset(0, -1), end: Offset.zero)
            .animate(CurvedAnimation(parent: anim, curve: Curves.easeOutCubic)),
        child: FadeTransition(opacity: anim, child: child),
      ),
    );
  }

  void _lookup() {
    final cs = Theme.of(context).colorScheme;
    final ctrl = TextEditingController();
    WordEntry? _result;
    var _loading = false;

    _showTopSheet(
      Align(
        alignment: Alignment.topCenter,
        child: Container(
          margin: const EdgeInsets.only(top: 56, left: 12, right: 12),
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: cs.surface,
            borderRadius: BorderRadius.circular(28),
          ),
          child: StatefulBuilder(
            builder: (ctx, setSheetState) {
              return Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text('查词', style: Theme.of(context).textTheme.headlineSmall),
                      const Spacer(),
                      IconButton(
                        icon: const Icon(Icons.close, size: 20),
                        onPressed: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: ctrl,
                    autofocus: true,
                    decoration: const InputDecoration(hintText: '输入单词'),
                    onSubmitted: (w) async {
                      if (w.trim().isEmpty) return;
                      setSheetState(() => _loading = true);
                      final entry = await _know.lookup(w.trim());
                      if (!mounted) return;
                      setSheetState(() { _result = entry; _loading = false; });
                    },
                  ),
                  const SizedBox(height: 16),
                  if (_loading)
                    const Center(child: CircularProgressIndicator())
                  else if (_result != null) ...[
                    if (_result!.phonetic case final p?) Text(p, style: TextStyle(color: cs.outline)),
                    if (_result!.partOfSpeech case final pos?)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Chip(
                          label: Text(pos),
                          backgroundColor: cs.primaryContainer,
                          labelStyle: TextStyle(color: cs.primary),
                        ),
                      ),
                    ..._result!.definitions.map((d) => Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: Text('• $d', style: TextStyle(height: 1.5)),
                        )),
                    if (_result!.examples.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Text('例句', style: TextStyle(fontWeight: FontWeight.w600, color: cs.primary)),
                      const SizedBox(height: 6),
                      ..._result!.examples.map((e) => Container(
                            width: double.infinity,
                            margin: const EdgeInsets.only(bottom: 6),
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: cs.surfaceContainerHighest,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(e, style: TextStyle(fontStyle: FontStyle.italic, height: 1.4)),
                          )),
                    ],
                  ],
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  void _plan() {
    final cs = Theme.of(context).colorScheme;
    final token = ApiClient().token;
    if (token == null) return;
    final personaId = context.read<PersonaProvider>().selected?.id;

    _showTopSheet(
      Align(
        alignment: Alignment.topCenter,
        child: Container(
          margin: const EdgeInsets.only(top: 56, left: 12, right: 12),
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: cs.surface,
            borderRadius: BorderRadius.circular(28),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text('学习计划', style: Theme.of(context).textTheme.headlineSmall),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              FutureBuilder(
                future: () async {
                  final svc = ProfileService(token: token);
                  final res = await Future.wait([
                    svc.getProfile(),
                    svc.getMistakes(),
                    if (personaId != null) svc.getEmotions(personaId) else Future.value(<dynamic>[]),
                  ]);
                  return res;
                }(),
                builder: (ctx, snap) {
                  if (snap.connectionState != ConnectionState.done) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snap.hasError) {
                    return Text('加载失败: ${snap.error}', style: TextStyle(color: cs.error));
                  }
                  final data = snap.data!;
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('📊 学习概览', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 12),
                      Text('此功能开发中，敬请期待'),
                    ],
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final chat = context.watch<ChatProvider>();
    final persona = context.watch<PersonaProvider>().selected;
    final msgs = chat.messages;

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // ── Top bar ──
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: cs.surface,
                border: Border(bottom: BorderSide(color: cs.outlineVariant.withAlpha(30))),
              ),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_ios_new, size: 20),
                    onPressed: () {
                      Navigator.of(context).pushAndRemoveUntil(
                        MaterialPageRoute(builder: (_) => const PersonaSelectScreen()),
                        (_) => false,
                      );
                    },
                  ),
                  Text(
                    persona?.roleEmoji ?? '🌟',
                    style: const TextStyle(fontSize: 24),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      persona?.name ?? 'Mellow',
                      style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.menu_book_outlined, color: cs.primary, size: 22),
                    onPressed: _lookup,
                  ),
                  IconButton(
                    icon: Icon(Icons.auto_graph_outlined, color: cs.primary, size: 22),
                    onPressed: _plan,
                  ),
                ],
              ),
            ),
            // ── Messages ──
            Expanded(
              child: msgs.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.chat_bubble_outline, size: 56, color: cs.outlineVariant.withAlpha(100)),
                          const SizedBox(height: 12),
                          Text(
                            '开始对话吧！',
                            style: theme.textTheme.bodyLarge?.copyWith(color: cs.outline),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      reverse: true,
                      controller: _scroll,
                      padding: const EdgeInsets.only(top: 12, bottom: 8),
                      itemCount: msgs.length + (chat.isStreaming ? 1 : 0),
                      itemBuilder: (_, i) {
                        if (chat.isStreaming && i == 0) return const TypingIndicator();
                        final idx = msgs.length - i - (chat.isStreaming ? 0 : 1);
                        return ChatBubble(
                          message: msgs[idx],
                          emoji: persona?.roleEmoji,
                          name: persona?.name,
                        );
                      },
                    ),
            ),
            // ── Input bar ──
            Container(
              padding: const EdgeInsets.fromLTRB(12, 8, 8, 12),
              decoration: BoxDecoration(
                color: cs.surface,
                border: Border(top: BorderSide(color: cs.outlineVariant.withAlpha(30))),
              ),
              child: Row(
                children: [
                  VoiceButton(onResult: (t) => _text.text = t),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: _text,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _send(),
                      maxLines: 4,
                      minLines: 1,
                      decoration: InputDecoration(
                        hintText: '说点什么...',
                        filled: true,
                        fillColor: cs.surfaceContainerHighest,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(28),
                          borderSide: BorderSide.none,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  GestureDetector(
                    onTap: _send,
                    child: Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        color: _text.text.trim().isNotEmpty ? cs.primary : cs.outlineVariant,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(Icons.send_rounded, size: 20, color: cs.onPrimary),
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
