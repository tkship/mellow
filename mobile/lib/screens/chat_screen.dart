import 'dart:ui';
import 'package:flutter/material.dart';
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
  void dispose() { _text.dispose(); _scroll.dispose(); super.dispose(); }

  void _send() {
    final t = _text.text.trim(); if (t.isEmpty) return;
    final p = context.read<PersonaProvider>().selected; if (p == null) return;
    context.read<ChatProvider>().sendMessage(p.id, t);
    _text.clear();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) _scroll.animateTo(0, duration: const Duration(milliseconds: 250), curve: Curves.easeOut);
    });
  }

  void _showSheet(Widget child) {
    showGeneralDialog(
      context: context, barrierDismissible: true, barrierColor: Colors.black.withAlpha(80),
      transitionDuration: const Duration(milliseconds: 350), pageBuilder: (_, __, ___) => child,
      transitionBuilder: (_, anim, __, child) => SlideTransition(
        position: Tween<Offset>(begin: const Offset(0, -1), end: Offset.zero).animate(CurvedAnimation(parent: anim, curve: Curves.easeOutCubic)),
        child: FadeTransition(opacity: anim, child: child),
      ),
    );
  }

  void _lookup() {
    final cs = Theme.of(context).colorScheme;
    final ctrl = TextEditingController();
    WordEntry? result;
    var loading = false;
    _showSheet(Align(
      alignment: Alignment.topCenter,
      child: Container(
        margin: const EdgeInsets.only(top: 56, left: 12, right: 12),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(color: cs.surface, borderRadius: BorderRadius.circular(28)),
        child: StatefulBuilder(builder: (ctx, setSt) {
          return Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [Text('查词', style: Theme.of(context).textTheme.headlineSmall), const Spacer(), IconButton(icon: const Icon(Icons.close, size: 20), onPressed: () => Navigator.pop(context))]),
            const SizedBox(height: 16),
            TextField(controller: ctrl, autofocus: true, decoration: InputDecoration(hintText: '输入单词', filled: true, fillColor: cs.surfaceContainerHighest, border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none)), onSubmitted: (w) async {
              if (w.trim().isEmpty) return;
              setSt(() => loading = true);
              result = await _know.lookup(w.trim());
              if (!mounted) return;
              setSt(() => loading = false);
            }),
            const SizedBox(height: 16),
            if (loading) const Center(child: CircularProgressIndicator()),
            if (result != null)
              _WordResult(result: result!, cs: cs),
          ]);
        }),
      ),
    ));
  }

  void _plan() {
    final cs = Theme.of(context).colorScheme;
    final token = ApiClient().token; if (token == null) return;
    _showSheet(Align(
      alignment: Alignment.topCenter,
      child: Container(
        margin: const EdgeInsets.only(top: 56, left: 12, right: 12), padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(color: cs.surface, borderRadius: BorderRadius.circular(28)),
        child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Text('学习计划', style: Theme.of(context).textTheme.headlineSmall), const Spacer(), IconButton(icon: const Icon(Icons.close, size: 20), onPressed: () => Navigator.pop(context))]),
          const SizedBox(height: 16),
          FutureBuilder(
            future: () async {
              final svc = ProfileService(token: token);
              return await Future.wait([svc.getProfile(), svc.getMistakes()]);
            }(),
            builder: (_, snap) {
              if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
              if (snap.hasError) return Text('加载失败', style: TextStyle(color: cs.error));
              return const Text('📊 学习计划功能开发中，敬请期待', style: TextStyle(height: 1.6));
            },
          ),
        ]),
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final chat = context.watch<ChatProvider>();
    final persona = context.watch<PersonaProvider>().selected;
    final msgs = chat.messages;

    return Scaffold(
      body: Column(children: [
        // ── Top bar with blur ──
        ClipRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
            child: Container(
              padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top, bottom: 8),
              decoration: BoxDecoration(color: cs.surface.withAlpha(180)),
              child: Row(children: [
                IconButton(icon: const Icon(Icons.arrow_back_ios_new, size: 20), onPressed: () => Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (_) => const PersonaSelectScreen()), (_) => false)),
                Text(persona?.roleEmoji ?? '🌟', style: const TextStyle(fontSize: 24)),
                const SizedBox(width: 8),
                Expanded(child: Text(persona?.name ?? 'Mellow', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700))),
                IconButton(icon: Icon(Icons.menu_book_outlined, color: cs.primary, size: 22), onPressed: _lookup),
                IconButton(icon: Icon(Icons.auto_graph_outlined, color: cs.primary, size: 22), onPressed: _plan),
              ]),
            ),
          ),
        ),
        // ── Messages ──
        Expanded(
          child: msgs.isEmpty
              ? Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
                  Icon(Icons.chat_bubble_outline, size: 48, color: cs.outlineVariant.withAlpha(80)),
                  const SizedBox(height: 10),
                  Text('开始对话吧！', style: theme.textTheme.bodyLarge?.copyWith(color: cs.outline)),
                ]))
              : ListView.builder(
                  reverse: true, controller: _scroll,
                  padding: const EdgeInsets.only(top: 10, bottom: 6),
                  itemCount: msgs.length + (chat.isStreaming ? 1 : 0),
                  itemBuilder: (_, i) {
                    if (chat.isStreaming && i == 0) return const TypingIndicator();
                    final idx = msgs.length - i - (chat.isStreaming ? 0 : 1);
                    return ChatBubble(message: msgs[idx], emoji: persona?.roleEmoji, name: persona?.name);
                  },
                ),
        ),
        // ── Floating input ──
        Padding(
          padding: const EdgeInsets.fromLTRB(10, 6, 10, 10),
          child: ClipRect(
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                decoration: BoxDecoration(color: cs.surface.withAlpha(200), borderRadius: BorderRadius.circular(28)),
                child: Row(children: [
                  VoiceButton(onResult: (t) => _text.text = t),
                  const SizedBox(width: 6),
                  Expanded(
                    child: TextField(
                      controller: _text, textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _send(), maxLines: 4, minLines: 1,
                      decoration: InputDecoration(
                        hintText: '说点什么...', filled: true, fillColor: cs.surfaceContainerHighest,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none),
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  GestureDetector(
                    onTap: _send,
                    child: Container(
                      width: 44, height: 44,
                      decoration: BoxDecoration(
                        color: _text.text.trim().isNotEmpty ? cs.primary : cs.outlineVariant,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(Icons.send_rounded, size: 20, color: cs.onPrimary),
                    ),
                  ),
                ]),
              ),
            ),
          ),
        ),
      ]),
    );
  }
}

class _WordResult extends StatelessWidget {
  const _WordResult({required this.result, required this.cs});
  final WordEntry result;
  final ColorScheme cs;
  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      if (result.phonetic case final p?) Text(p, style: TextStyle(color: cs.outline)),
      if (result.partOfSpeech case final pos?)
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(color: cs.primaryContainer, borderRadius: BorderRadius.circular(10)),
            child: Text(pos, style: TextStyle(color: cs.primary)),
          ),
        ),
      ...result.definitions.map((d) => Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text('• $d', style: const TextStyle(height: 1.5)),
          )),
      if (result.examples.isNotEmpty) ...[
        const SizedBox(height: 10),
        Text('例句', style: TextStyle(fontWeight: FontWeight.w600, color: cs.primary)),
        const SizedBox(height: 6),
        ...result.examples.map((e) => Container(
              width: double.infinity,
              margin: const EdgeInsets.only(bottom: 6),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: cs.surfaceContainerHighest, borderRadius: BorderRadius.circular(12)),
              child: Text(e, style: const TextStyle(fontStyle: FontStyle.italic, height: 1.4)),
            )),
      ],
    ]);
  }
}
