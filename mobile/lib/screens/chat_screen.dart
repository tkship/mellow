import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';

import '../config/api_config.dart';
import '../providers/chat_provider.dart';
import '../providers/persona_provider.dart';
import '../services/api_client.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/typing_indicator.dart';
import '../services/profile_service.dart';
import '../widgets/voice_button.dart';
import 'persona_select_screen.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _textCtrl = TextEditingController();
  final _scrollCtrl = ScrollController();
  final _inputFocus = FocusNode();
  bool _inputFocused = false;

  @override
  void initState() {
    super.initState();
    _inputFocus.addListener(() {
      if (mounted) setState(() => _inputFocused = _inputFocus.hasFocus);
    });
  }

  void _sendMessage() {
    final text = _textCtrl.text.trim();
    if (text.isEmpty) return;
    final persona = context.read<PersonaProvider>().selected;
    if (persona == null) return;
    context.read<ChatProvider>().sendMessage(persona.id, text);
    _textCtrl.clear();
  }

  void _onVoiceResult(String text) {
    if (text.isNotEmpty) {
      _textCtrl.text = text;
      _sendMessage();
    }
  }

  @override
  void dispose() {
    _textCtrl.dispose();
    _scrollCtrl.dispose();
    _inputFocus.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chat = context.watch<ChatProvider>();
    final persona = context.watch<PersonaProvider>().selected;
    final theme = Theme.of(context);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            Navigator.of(context).pushAndRemoveUntil(
              MaterialPageRoute(builder: (_) => const PersonaSelectScreen()),
              (_) => false,
            );
          },
        ),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                theme.colorScheme.primaryContainer.withOpacity(0.55),
                theme.colorScheme.secondaryContainer.withOpacity(0.18),
                theme.colorScheme.surface,
              ],
              stops: const [0.0, 0.55, 1.0],
            ),
          ),
        ),
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        scrolledUnderElevation: 0,
        shape: Border(
          bottom: BorderSide(
            color: theme.colorScheme.outlineVariant.withOpacity(0.15),
            width: 0.5,
          ),
        ),
        title: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    theme.colorScheme.primaryContainer,
                    theme.colorScheme.secondaryContainer,
                  ],
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: theme.colorScheme.primary.withOpacity(0.15),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  persona?.roleEmoji ?? '🌟',
                  style: const TextStyle(fontSize: 18),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Text(
              persona?.name ?? 'Mellow',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        actions: [
          _ScaleIconButton(
            icon: Icon(Icons.book, color: theme.colorScheme.primary),
            tooltip: '学习计划',
            onPressed: () {
              Navigator.of(context).push(
                PageRouteBuilder(
                  opaque: false,
                  barrierDismissible: true,
                  barrierColor: Colors.black45,
                  transitionDuration: 200.ms,
                  pageBuilder: (_, __, ___) => SafeArea(
                    child: Align(
                      alignment: Alignment.topCenter,
                      child: Padding(
                        padding: const EdgeInsets.only(top: 16),
                        child: _LearningPlanSheet(),
                      ),
                    ),
                  ),
                  transitionsBuilder: (_, anim, __, child) =>
                      FadeTransition(opacity: anim, child: child),
                ),
              );
            },
          ),
          _ScaleIconButton(
            icon: Icon(Icons.search, color: theme.colorScheme.primary),
            tooltip: '查词',
            onPressed: () {
              final controller = TextEditingController();
              showGeneralDialog(
                context: context,
                barrierDismissible: true,
                barrierLabel: '查词',
                barrierColor: Colors.black38,
                transitionDuration: 200.ms,
                pageBuilder: (ctx, __, ___) => SafeArea(
                  child: Align(
                    alignment: Alignment.topCenter,
                    child: Padding(
                      padding: const EdgeInsets.only(top: 16),
                      child: AlertDialog(
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20)),
                  title: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: Theme.of(ctx).colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(Icons.translate,
                            color: Theme.of(ctx).colorScheme.primary, size: 22),
                      ),
                      const SizedBox(width: 12),
                      const Text('查词'),
                    ],
                  ),
                  content: TextField(
                    controller: controller,
                    autofocus: true,
                    textInputAction: TextInputAction.search,
                    decoration: InputDecoration(
                      hintText: '输入英语单词...',
                      prefixIcon: const Icon(Icons.search),
                      filled: true,
                      fillColor:
                          Theme.of(ctx).colorScheme.surfaceContainerHighest,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide.none,
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide(
                          color: Theme.of(ctx).colorScheme.primary,
                          width: 2,
                        ),
                      ),
                    ),
                    onSubmitted: (word) {
                      Navigator.pop(ctx);
                      _lookupWord(word);
                    },
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(ctx),
                      child: const Text('取消'),
                    ),
                    FilledButton(
                      onPressed: () {
                        Navigator.pop(ctx);
                        _lookupWord(controller.text.trim());
                      },
                      child: const Text('查询'),
                    ),
                  ],
                ),
              ),
            ),
          ),
          transitionBuilder: (_, anim, __, child) =>
              FadeTransition(opacity: anim, child: child),
        );
            },
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              theme.colorScheme.surface,
              theme.colorScheme.primaryContainer.withOpacity(0.05),
              theme.colorScheme.secondaryContainer.withOpacity(0.04),
            ],
            stops: const [0.0, 0.5, 1.0],
          ),
        ),
        child: Stack(
          children: [
            // Subtle dot pattern texture
            Positioned.fill(
              child: IgnorePointer(
                child: CustomPaint(
                  painter: _DotPatternPainter(
                    color: theme.colorScheme.primary.withOpacity(0.04),
                    spacing: 24,
                    radius: 1.2,
                  ),
                ),
              ),
            ),
            // Main content column
            Column(
              children: [
            Expanded(
              child: chat.messages.isEmpty
                  ? _buildEmptyState(theme, persona?.name ?? 'Mellow')
                  : ListView.builder(
                      controller: _scrollCtrl,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 12),
                      itemCount: chat.messages.length,
                      itemBuilder: (_, i) => Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: ChatBubble(
                          message: chat.messages[i],
                          personaEmoji: persona?.roleEmoji,
                          personaName: persona?.name,
                        ),
                      ),
                    ),
            ),
            if (chat.isStreaming) const TypingIndicator(),
            _buildInputBar(theme),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(ThemeData theme, String personaName) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Decorative glow behind icon
          Stack(
            alignment: Alignment.center,
            children: [
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      theme.colorScheme.primary.withOpacity(0.12),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
              Container(
                width: 80,
                height: 80,
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
                    BoxShadow(
                      color: theme.colorScheme.tertiary.withOpacity(0.12),
                      blurRadius: 36,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Icon(Icons.chat_bubble_rounded,
                    size: 36, color: theme.colorScheme.primary),
              ),
            ],
          )
              .animate(onPlay: (ctrl) => ctrl.repeat(reverse: true))
              .scale(
                begin: const Offset(0.92, 0.92),
                end: const Offset(1.06, 1.06),
                duration: 1500.ms,
                curve: Curves.easeInOut,
              ),
          const SizedBox(height: 32),
          Text(
            '和 $personaName 开始对话吧',
            style: theme.textTheme.titleLarge?.copyWith(
              color: theme.colorScheme.onSurface,
              fontWeight: FontWeight.w600,
              height: 1.3,
            ),
          )
              .animate()
              .fadeIn(delay: 300.ms)
              .slideY(begin: 12),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer.withOpacity(0.4),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              '试着用英语聊聊吧！',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w500,
              ),
            ),
          ).animate().fadeIn(delay: 500.ms).scale(
                begin: const Offset(0.9, 0.9),
                curve: Curves.elasticOut,
              ),
        ],
      ),
    );
  }

  Widget _buildInputBar(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            theme.colorScheme.primaryContainer.withOpacity(0.10),
            theme.colorScheme.surface,
          ],
        ),
        border: Border(
          top: BorderSide(
            color: _inputFocused
                ? theme.colorScheme.primary.withOpacity(0.12)
                : theme.colorScheme.outlineVariant.withOpacity(0.15),
            width: _inputFocused ? 1.2 : 0.5,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: theme.colorScheme.primary
                .withOpacity(_inputFocused ? 0.10 : 0.02),
            blurRadius: _inputFocused ? 16 : 6,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          VoiceButton(onResult: _onVoiceResult),
          const SizedBox(width: 8),
          Expanded(
            child: AnimatedContainer(
              duration: 200.ms,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                boxShadow: _inputFocused
                    ? [
                        BoxShadow(
                          color: theme.colorScheme.primary.withOpacity(0.15),
                          blurRadius: 8,
                          spreadRadius: 1,
                        ),
                      ]
                    : [],
              ),
              child: TextField(
                controller: _textCtrl,
                focusNode: _inputFocus,
                style: theme.textTheme.bodyMedium,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: theme.colorScheme.surfaceContainerHighest,
                  hintText: '输入消息...',
                  hintStyle: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                  border: OutlineInputBorder(
                    borderRadius:
                        const BorderRadius.all(Radius.circular(24)),
                    borderSide: BorderSide(
                      color: _inputFocused
                          ? theme.colorScheme.primary.withOpacity(0.3)
                          : Colors.transparent,
                      width: _inputFocused ? 1.5 : 0,
                    ),
                  ),
                  enabledBorder: const OutlineInputBorder(
                    borderRadius: BorderRadius.all(Radius.circular(24)),
                    borderSide: BorderSide.none,
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius:
                        const BorderRadius.all(Radius.circular(24)),
                    borderSide: BorderSide(
                      color: theme.colorScheme.primary,
                      width: 2,
                    ),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 12),
                ),
                onSubmitted: (_) => _sendMessage(),
              ),
            ),
          ),
          const SizedBox(width: 8),
          _SendButton(onPressed: _sendMessage, theme: theme),
        ],
      ),
    );
  }

  void _lookupWord(String word) async {
    if (word.isEmpty) return;
    try {
      final dio = Dio(BaseOptions(baseUrl: ApiConfig.baseUrl));
      final token = ApiClient().token;
      final response = await dio.get(
        '${ApiConfig.knowledgeUrl}/lookup',
        queryParameters: {'word': word},
        options: Options(
            headers:
                token != null ? {'Authorization': 'Bearer $token'} : {}),
      );
      if (!mounted) return;
      final data = response.data;
      if (data['error'] != null) {
        if (mounted) {
          ScaffoldMessenger.of(context)
              .showSnackBar(SnackBar(content: Text('未找到 "$word"')));
        }
        return;
      }

      if (!mounted) return;
      final theme = Theme.of(context);
      final resultWord = data['word'] as String? ?? word;
      final phonetic = data['phonetic'] as String?;
      final pos = data['part_of_speech'] as String?;
      final defs = (data['definitions'] as List<dynamic>?)
              ?.map((d) => d.toString())
              .toList() ??
          [];
      final examples = (data['examples'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [];

      if (!mounted) return;
      showGeneralDialog(
        context: context,
        barrierDismissible: true,
        barrierLabel: '查词结果',
        barrierColor: Colors.black38,
        transitionDuration: 200.ms,
        pageBuilder: (_, __, ___) => SafeArea(
          child: Align(
            alignment: Alignment.topCenter,
            child: Padding(
              padding: const EdgeInsets.only(top: 16),
              child: AlertDialog(
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(resultWord,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  )),
              if (phonetic != null) ...[
                const SizedBox(height: 4),
                Text(phonetic,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.outline,
                      fontStyle: FontStyle.italic,
                    )),
              ],
              const SizedBox(height: 8),
              Divider(
                  color: theme.colorScheme.outlineVariant.withOpacity(0.3)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (pos != null) ...[
                  Wrap(spacing: 6, children: [
                    Chip(
                      avatar: Icon(Icons.category,
                          size: 16, color: theme.colorScheme.primary),
                      label: Text(pos),
                      backgroundColor: theme.colorScheme.primaryContainer,
                      side: BorderSide.none,
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                    ),
                  ]),
                  const SizedBox(height: 16),
                ],
                if (defs.isNotEmpty) ...[
                  Text('释义',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: theme.colorScheme.primary,
                      )),
                  const SizedBox(height: 8),
                  ...defs.map((d) => Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              margin: const EdgeInsets.only(top: 7),
                              width: 6,
                              height: 6,
                              decoration: BoxDecoration(
                                color: theme.colorScheme.primary,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                                child:
                                    Text(d, style: theme.textTheme.bodyLarge)),
                          ],
                        ),
                      )),
                ],
                if (examples.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Text('例句',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: theme.colorScheme.primary,
                      )),
                  const SizedBox(height: 8),
                  ...examples.map((e) => Container(
                        margin: const EdgeInsets.only(bottom: 6),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(12),
                          border: Border(
                            left: BorderSide(
                              color:
                                  theme.colorScheme.primary.withOpacity(0.4),
                              width: 3,
                            ),
                          ),
                        ),
                        child: Text(
                          '"$e"',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontStyle: FontStyle.italic,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      )),
                ],
              ],
            ),
          ),
          actions: [
            FilledButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('关闭'),
            ),
          ],
        ).animate().fadeIn(duration: 250.ms).scale(
              begin: const Offset(0.95, 0.95), curve: Curves.easeOutBack),
          ),
        ),
      ),
      transitionBuilder: (_, anim, __, child) =>
              FadeTransition(opacity: anim, child: child),
      );
    } catch (e) {
      if (mounted) {
        String msg = '查询失败，请稍后重试';
        if (e is DioException) {
          if (e.response?.statusCode == 404) {
            msg = '未找到 "$word"';
          } else if (e.type == DioExceptionType.connectionTimeout) {
            msg = '连接超时，请检查网络';
          }
        }
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg)),
        );
      }
    }
  }
}

// ─── Scale-on-press icon button ─────────────────────────────────────
class _ScaleIconButton extends StatefulWidget {
  final Widget icon;
  final String? tooltip;
  final VoidCallback? onPressed;

  const _ScaleIconButton({required this.icon, this.tooltip, this.onPressed});

  @override
  State<_ScaleIconButton> createState() => _ScaleIconButtonState();
}

class _ScaleIconButtonState extends State<_ScaleIconButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 200),
    );
    _scale = Tween<double>(begin: 1.0, end: 0.85).animate(
      CurvedAnimation(parent: _ctrl, curve: Curves.easeOut),
    );
    _ctrl.addStatusListener((s) {
      if (s == AnimationStatus.completed) _ctrl.reverse();
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _scale,
      builder: (_, child) => Transform.scale(scale: _scale.value, child: child),
      child: IconButton(
        icon: widget.icon,
        tooltip: widget.tooltip,
        onPressed: () {
          _ctrl.forward();
          widget.onPressed?.call();
        },
      ),
    );
  }
}

// ─── Send button with rotation on press ─────────────────────────────
class _SendButton extends StatefulWidget {
  final VoidCallback? onPressed;
  final ThemeData theme;

  const _SendButton({required this.onPressed, required this.theme});

  @override
  State<_SendButton> createState() => _SendButtonState();
}

class _SendButtonState extends State<_SendButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _rotation;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
    );
    _rotation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: 0.15), weight: 1),
      TweenSequenceItem(tween: Tween(begin: 0.15, end: 0.0), weight: 2),
    ]).animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOutBack));
    _ctrl.addStatusListener((s) {
      if (s == AnimationStatus.completed) _ctrl.reset();
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _rotation,
      builder: (_, child) => Transform.rotate(
        angle: _rotation.value * 3.14,
        child: child,
      ),
      child: IconButton.filled(
        onPressed: () {
          _ctrl.forward(from: 0.0);
          widget.onPressed?.call();
        },
        icon: const Icon(Icons.send),
        style: IconButton.styleFrom(
          backgroundColor: widget.theme.colorScheme.primary,
          foregroundColor: widget.theme.colorScheme.onPrimary,
          shape: const CircleBorder(),
        ),
      ),
    );
  }
}

// ─── Learning plan sheet (as dialog content) ────────────────────────
class _LearningPlanSheet extends StatefulWidget {
  const _LearningPlanSheet();

  @override
  State<_LearningPlanSheet> createState() => _LearningPlanSheetState();
}

class _LearningPlanSheetState extends State<_LearningPlanSheet>
    with SingleTickerProviderStateMixin {
  late final TabController _tabCtrl;
  Map<String, dynamic>? _profile;
  List<dynamic>? _mistakes;
  List<dynamic>? _emotions;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    try {
      final token = ApiClient().token;
      final service = ProfileService(token: token);
      final personaId = context.read<PersonaProvider>().selected?.id;

      final results = await Future.wait([
        service.getProfile(),
        service.getMistakes(),
        if (personaId != null)
          service.getEmotions(personaId)
        else
          Future.value(<dynamic>[]),
      ]);

      if (mounted) {
        setState(() {
          _profile = results[0] as Map<String, dynamic>;
          _mistakes = results[1] as List<dynamic>;
          _emotions = results[2] as List<dynamic>;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenHeight = MediaQuery.of(context).size.height;
    final screenWidth = MediaQuery.of(context).size.width;

    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(24),
      child: AnimatedContainer(
        duration: 300.ms,
        width: screenWidth - 48 < 500 ? screenWidth - 48 : 500,
        height: screenHeight * 0.62,
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24),
          color: theme.colorScheme.surface,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.fromLTRB(20, 16, 8, 8),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(
                    color: theme.colorScheme.outlineVariant.withOpacity(0.3),
                  ),
                ),
              ),
              child: Row(
                children: [
                  Icon(Icons.auto_stories,
                      color: theme.colorScheme.primary, size: 24),
                  const SizedBox(width: 8),
                  Text('📚 学习记录',
                      style: theme.textTheme.titleLarge
                          ?.copyWith(fontWeight: FontWeight.w600)),
                  const Spacer(),
                  if (_loading)
                    const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  else
                    IconButton(
                      icon: Icon(Icons.refresh,
                          size: 20, color: theme.colorScheme.primary),
                      tooltip: '刷新',
                      onPressed: () {
                        setState(() {
                          _loading = true;
                          _error = null;
                        });
                        _loadData();
                      },
                    ),
                  IconButton(
                    icon: Icon(Icons.close,
                        size: 20, color: theme.colorScheme.outline),
                    tooltip: '关闭',
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),
            TabBar(
              controller: _tabCtrl,
              labelColor: theme.colorScheme.primary,
              unselectedLabelColor: theme.colorScheme.outline,
              indicatorSize: TabBarIndicatorSize.tab,
              tabs: const [
                Tab(text: '概览'),
                Tab(text: '错误记录'),
                Tab(text: '情绪轨迹'),
              ],
            ),
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : _error != null
                      ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.error_outline,
                                    size: 48,
                                    color: theme.colorScheme.error),
                                const SizedBox(height: 12),
                                Text('加载失败',
                                    style: theme.textTheme.titleMedium
                                        ?.copyWith(
                                            color: theme.colorScheme.error)),
                                const SizedBox(height: 8),
                                Text(_error!,
                                    style: theme.textTheme.bodySmall?.copyWith(
                                        color: theme
                                            .colorScheme.onSurfaceVariant),
                                    textAlign: TextAlign.center),
                                const SizedBox(height: 16),
                                FilledButton.tonal(
                                  onPressed: () {
                                    setState(() {
                                      _loading = true;
                                      _error = null;
                                    });
                                    _loadData();
                                  },
                                  child: const Text('重试'),
                                ),
                              ],
                            ),
                          ),
                        )
                      : TabBarView(
                          controller: _tabCtrl,
                          children: [
                            _buildOverviewTab(theme),
                            _buildMistakesTab(theme),
                            _buildEmotionsTab(theme),
                          ],
                        ),
            ),
          ],
        ),
      ).animate().fadeIn(duration: 300.ms).scale(
            begin: const Offset(0.95, 0.95), curve: Curves.easeOutBack),
    );
  }

  Widget _buildOverviewTab(ThemeData theme) {
    final p = _profile ?? {};
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildStatCard(theme, Icons.school, 'CEFR 等级',
            p['cefr_level']?.toString() ?? '未知'),
        _buildStatCard(theme, Icons.translate, '词汇量',
            '~${p['vocabulary_size'] ?? 0}'),
        _buildStatCard(theme, Icons.check_circle, '已掌握单词',
            '${p['known_words_count'] ?? 0} 个'),
        if (p['weak_areas'] != null &&
            (p['weak_areas'] as List).isNotEmpty)
          _buildStatCard(theme, Icons.warning_amber, '薄弱环节',
              (p['weak_areas'] as List).join(', ')),
        if (p['summary'] != null && p['summary'].toString().isNotEmpty)
          Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('学习摘要', style: theme.textTheme.titleSmall),
                  const SizedBox(height: 8),
                  Text(p['summary'].toString(),
                      style: theme.textTheme.bodyMedium),
                ],
              ),
            ),
          ),
        if (p['completed_lessons'] != null &&
            (p['completed_lessons'] as List).isNotEmpty)
          Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('最近完成', style: theme.textTheme.titleSmall),
                  const SizedBox(height: 8),
                  ...(p['completed_lessons'] as List).map((l) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(children: [
                          Icon(Icons.check,
                              size: 16, color: theme.colorScheme.primary),
                          const SizedBox(width: 8),
                          Text(l.toString(),
                              style: theme.textTheme.bodyMedium),
                        ]),
                      )),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildMistakesTab(ThemeData theme) {
    final mistakes = _mistakes ?? [];
    if (mistakes.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.auto_fix_high,
                size: 48, color: theme.colorScheme.outline),
            const SizedBox(height: 12),
            Text('暂无错误记录',
                style: theme.textTheme.bodyLarge
                    ?.copyWith(color: theme.colorScheme.outline)),
            const SizedBox(height: 4),
            Text('继续对话，AI 会自动记录你的错误',
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: theme.colorScheme.outline)),
          ],
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: mistakes.length,
      itemBuilder: (_, i) {
        final m = mistakes[i] as Map<String, dynamic>;
        final word = m['word_or_rule'] ?? '';
        final type = m['mistake_type'] ?? '';
        final correction = m['correction'] ?? '';
        return Card(
          margin: const EdgeInsets.only(bottom: 10),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.errorContainer,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(word,
                        style: theme.textTheme.labelMedium?.copyWith(
                            color: theme.colorScheme.onErrorContainer)),
                  ),
                  const SizedBox(width: 8),
                  Text(type,
                      style: theme.textTheme.bodySmall
                          ?.copyWith(color: theme.colorScheme.outline)),
                ]),
                if (correction.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text('✅ $correction', style: theme.textTheme.bodyMedium),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildEmotionsTab(ThemeData theme) {
    final emotions = _emotions ?? [];
    if (emotions.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.mood, size: 48, color: theme.colorScheme.outline),
            const SizedBox(height: 12),
            Text('暂无情绪记录',
                style: theme.textTheme.bodyLarge
                    ?.copyWith(color: theme.colorScheme.outline)),
            const SizedBox(height: 4),
            Text('继续对话，AI 会感知你的学习情绪',
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: theme.colorScheme.outline)),
          ],
        ),
      );
    }

    String moodEmoji(String mood) {
      switch (mood) {
        case 'happy':
          return '😊';
        case 'excited':
          return '🤩';
        case 'neutral':
          return '😐';
        case 'frustrated':
          return '😤';
        case 'sad':
          return '😢';
        case 'confident':
          return '💪';
        case 'anxious':
          return '😰';
        default:
          return '❓';
      }
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: emotions.length,
      itemBuilder: (_, i) {
        final e = emotions[i] as Map<String, dynamic>;
        final mood = e['mood'] ?? 'neutral';
        final reason = e['reason'] ?? '';
        final date = e['date'] ?? '';
        final intensity = (e['intensity'] ?? 0.5).toDouble();

        return Card(
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            leading: Text(moodEmoji(mood.toString()),
                style: const TextStyle(fontSize: 28)),
            title: Row(children: [
              Text(mood.toString(),
                  style: theme.textTheme.bodyLarge
                      ?.copyWith(fontWeight: FontWeight.w600)),
              const SizedBox(width: 8),
              Expanded(
                child: LinearProgressIndicator(
                  value: intensity,
                  backgroundColor:
                      theme.colorScheme.surfaceContainerHighest,
                  color: intensity > 0.7
                      ? theme.colorScheme.error
                      : intensity > 0.4
                          ? theme.colorScheme.tertiary
                          : theme.colorScheme.primary,
                  minHeight: 4,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ]),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (reason.toString().isNotEmpty)
                  Text(reason.toString(),
                      style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant)),
                Text(date.toString(),
                    style: theme.textTheme.labelSmall
                        ?.copyWith(color: theme.colorScheme.outline)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatCard(
      ThemeData theme, IconData icon, String label, String value) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Icon(icon, color: theme.colorScheme.primary),
        title: Text(label,
            style: theme.textTheme.bodySmall
                ?.copyWith(color: theme.colorScheme.outline)),
        subtitle: Text(value, style: theme.textTheme.bodyLarge),
      ),
    );
  }
}

// ─── Dot pattern background painter ─────────────────────────────────
class _DotPatternPainter extends CustomPainter {
  final Color color;
  final double spacing;
  final double radius;

  _DotPatternPainter({
    required this.color,
    this.spacing = 24,
    this.radius = 1.2,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;
    final cols = (size.width / spacing).ceil();
    final rows = (size.height / spacing).ceil();
    for (int y = 0; y < rows; y++) {
      for (int x = 0; x < cols; x++) {
        canvas.drawCircle(
          Offset(x * spacing + spacing / 2, y * spacing + spacing / 2),
          radius,
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _DotPatternPainter old) =>
      old.color != color || old.spacing != spacing || old.radius != radius;
}
