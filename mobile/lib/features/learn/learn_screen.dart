import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../models/learning_stats.dart';
import '../../providers/learn_provider.dart';
import '../../services/api_client.dart';
import '../../shared/constants/ui_strings.dart';
import '../../shared/constants/error_messages.dart';
import '../../shared/widgets/mellow_logo.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';
import '../../shared/vignettes/spending_tracker/components/circle_percentage_widget.dart';
import '../../shared/vignettes/drink_rewards_list/drink_card.dart';
import '../../shared/vignettes/drink_rewards_list/drink_data.dart';
import '../../shared/vignettes/sparkle_party/fx_renderer.dart';
import '../../shared/vignettes/sparkle_party/fx_entry.dart';
import '../../shared/vignettes/sparkle_party/particlefx/fireworks.dart';
import '../../shared/vignettes/sparkle_party/utils/sprite_sheet.dart';

/// 学习页 — 进度 / 生词本 / 错题 三 Tab 容器
class LearnScreen extends ConsumerStatefulWidget {
  const LearnScreen({super.key});

  @override
  ConsumerState<LearnScreen> createState() => _LearnScreenState();
}

class _LearnScreenState extends ConsumerState<LearnScreen>
    with SingleTickerProviderStateMixin {
  int _currentTab = 0;
  bool _vocabFetched = false;
  bool _mistakesLoading = false;
  String _vocabSort = 'recent';
  final _searchController = TextEditingController();
  bool _showCelebration = false;
  Timer? _searchDebounce;
  List<WordEntry> _searchResults = [];
  bool _isSearching = false;

  static const _tabLabels = [MellowStrings.progress, MellowStrings.vocabBook, MellowStrings.mistakes];
  static const _tabValues = ['progress', 'vocab', 'mistakes'];

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(learnProvider.notifier).fetchStats();
    });
  }

  @override
  void dispose() {
    _searchDebounce?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  void _onTabChanged(String value) {
    final index = _tabValues.indexOf(value);
    if (index == _currentTab) return;
    setState(() => _currentTab = index);

    if (value == 'vocab' && !_vocabFetched) {
      _vocabFetched = true;
      ref.read(learnProvider.notifier).fetchVocab(sort: _vocabSort);
    } else if (value == 'mistakes') {
      _loadMistakes();
    }
  }

  Future<void> _loadMistakes() async {
    if (_mistakesLoading) return;
    setState(() => _mistakesLoading = true);
    try {
      await ref.read(learnProvider.notifier).fetchMistakes();
      if (!mounted) return;
    } finally {
      if (mounted) {
        setState(() => _mistakesLoading = false);
      }
    }
  }

  void _onSortChanged(String sort) {
    if (sort == _vocabSort) return;
    setState(() => _vocabSort = sort);
    ref.read(learnProvider.notifier).fetchVocab(sort: sort);
  }

  Future<void> _performSearch(String query) async {
    setState(() => _isSearching = true);
    try {
      final client = ref.read(apiClientProvider);
      final res = await client.searchVocabulary(query);
      final data = res.data as Map<String, dynamic>?;
      final results = (data?['results'] as List?)
              ?.map((e) => WordEntry.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [];
      if (mounted) {
        setState(() {
          _searchResults = results;
          _isSearching = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isSearching = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('搜索失败，请重试')),
        );
      }
    }
  }

  void _showWordDetail(WordEntry word) {
    final theme = Theme.of(context);
    showShadSheet(
      context: context,
      builder: (ctx) => _WordDetailSheet(word: word, theme: theme),
    );
  }

  Future<void> _deleteWord(WordEntry word) async {
    await ref.read(learnProvider.notifier).deleteVocab(word.word);
    if (!mounted) return;
    final error = ref.read(learnProvider).error;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error)),
      );
    }
  }

  void _triggerCelebration() {
    setState(() => _showCelebration = true);
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) setState(() => _showCelebration = false);
    });
  }

  double _cefrProgress(LearningStats stats) {
    final list = stats.cefrProgress;
    if (list.isEmpty) return 0.0;
    return list.last.score.clamp(0.0, 1.0);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(learnProvider);
    final theme = Theme.of(context);

    return Stack(
      children: [
        Scaffold(
      backgroundColor: theme.colorScheme.surface,
      appBar: AppBar(
        title: Text(
          MellowStrings.learn,
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(44),
          child: _buildTabBar(theme),
        ),
      ),
      body: SafeArea(
        child: IndexedStack(
        index: _currentTab,
        children: [
          _buildProgressContent(state, theme),
          _buildVocabContent(state, theme),
          _buildMistakesContent(state, theme),
        ],
        ),
      ),
    ),
    if (_showCelebration)
      Positioned.fill(
        child: IgnorePointer(
          child: FxRenderer(
            fx: FXEntry('fireworks',
                create: (sheet, size) =>
                    Fireworks(spriteSheet: sheet, size: size)),
            size: MediaQuery.of(context).size,
            spriteSheet: SpriteSheet(
              imageProvider: const AssetImage(
                  'assets/vignettes/sparkle_party/sparkleparty_spritesheet_2.png'),
              length: 16,
              frameWidth: 32,
            ),
          ),
        ),
      ),
  ],
);
  }

  // ── 自定义 Tab 栏（品牌绿激活指示器） ──

  Widget _buildTabBar(ThemeData theme) {
    return Row(
      children: List.generate(_tabLabels.length, (i) {
        final selected = i == _currentTab;
        return Expanded(
          child: GestureDetector(
            onTap: () => _onTabChanged(_tabValues[i]),
            behavior: HitTestBehavior.opaque,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  child: Text(
                    _tabLabels[i],
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
                      color: selected
                          ? MellowColors.brandGreen
                          : theme.colorScheme.onSurface.withAlpha(140),
                    ),
                  ),
                ),
                AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  height: selected ? 2.5 : 0,
                  width: selected ? 28 : 0,
                  decoration: BoxDecoration(
                    color: MellowColors.brandGreen,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ],
            ),
          ),
        );
      }),
    );
  }

  // ═══════════════════ 进度 Tab ═══════════════════

  Widget _buildProgressContent(LearnState state, ThemeData theme) {
    final stats = state.stats;
    final showShimmer = state.isLoading && stats == null;

    if (showShimmer) {
      return _buildShimmerProgress();
    }

    if (stats == null) {
      return _buildErrorRetry(
        message: state.error ?? MellowErrors.loadFailed,
        onRetry: () => ref.read(learnProvider.notifier).fetchStats(),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(MellowSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // ── 三张统计卡片 ──
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  label: MellowStrings.cefrLevel,
                  value: stats.cefrLevel,
                  icon: LucideIcons.award,
                  iconColor: MellowColors.starBlue,
                ),
              ),
              const SizedBox(width: MellowSpacing.sm),
              Expanded(
                child: _StatCard(
                  label: MellowStrings.vocabCount,
                  value: '${stats.vocabCount}',
                  icon: LucideIcons.bookOpen,
                  iconColor: MellowColors.brandGreen,
                ),
              ),
              const SizedBox(width: MellowSpacing.sm),
              Expanded(
                child: _StatCard(
                  label: MellowStrings.learningDays,
                  value: '${stats.learningDays}',
                  icon: LucideIcons.calendarDays,
                  iconColor: MellowColors.brandOrange,
                ),
              ),
            ],
          ),
          const SizedBox(height: MellowSpacing.lg),

          // ── 时间范围切换 ──
          _buildRangeSelector(state.range),
          const SizedBox(height: MellowSpacing.lg),

          // ── CEFR 进度图表 ──
          Container(
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              borderRadius:
                  BorderRadius.circular(MellowSpacing.radiusLg),
              border: Border.all(
                color: MellowColors.border(context).withAlpha(100),
              ),
            ),
            padding: const EdgeInsets.all(MellowSpacing.md),
            child: Center(
              child: CirclePercentageWidget(
                title: stats.cefrLevel,
                percent: _cefrProgress(stats),
                color0: MellowColors.brandGreen,
                color1: MellowColors.brandGreen.withAlpha(100),
              ),
            ),
          ),
          const SizedBox(height: MellowSpacing.lg),

          // ── 薄弱项 ──
          if (stats.weakAreas.isNotEmpty) ...[
            _SectionTitle(title: MellowStrings.weakAreas),
            const SizedBox(height: MellowSpacing.sm),
            ...stats.weakAreas.map(_buildWeakAreaBar),
            const SizedBox(height: MellowSpacing.lg),
          ],

          // ── 学习计划卡片 ──
          ..._buildLearningPlanCards(),
          const SizedBox(height: MellowSpacing.lg),

          // ── 完成今日任务按钮 ──
          SizedBox(
            height: 48,
            child: ShadButton(
              onPressed: _triggerCelebration,
              child: const Text(
                MellowStrings.completeToday,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          const SizedBox(height: MellowSpacing.md),
        ],
      ),
    );
  }

  // ── 时间范围分段控件 ──

  Widget _buildRangeSelector(String currentRange) {
    final ranges = [
      ('week', MellowStrings.week),
      ('month', MellowStrings.month),
      ('half_year', MellowStrings.halfYear),
    ];

    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(MellowSpacing.radiusMd),
        border: Border.all(
          color: MellowColors.border(context).withAlpha(120),
        ),
      ),
      child: Row(
        children: ranges.map((r) {
          final selected = currentRange == r.$1;
          return Expanded(
            child: GestureDetector(
              onTap: () =>
                  ref.read(learnProvider.notifier).setRange(r.$1),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  color: selected
                      ? MellowColors.brandGreen
                      : Colors.transparent,
                  borderRadius:
                      BorderRadius.circular(MellowSpacing.radiusSm),
                ),
                alignment: Alignment.center,
                child: Text(
                  r.$2,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight:
                        selected ? FontWeight.w600 : FontWeight.w400,
                    color: selected ? Colors.white : null,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // ── 薄弱项进度条 ──

  Widget _buildWeakAreaBar(String area) {
    final theme = Theme.of(context);
    // 根据名称哈希生成一个模拟进度值（50–95%）
    final progress = 0.5 + (area.hashCode % 45) / 100.0;

    return Padding(
      padding: const EdgeInsets.only(bottom: MellowSpacing.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                area,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${(progress * 100).toInt()}%',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: MellowColors.brandGreen,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          ClipRRect(
            borderRadius:
                BorderRadius.circular(MellowSpacing.radiusFull),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 8,
              backgroundColor:
                  theme.colorScheme.onSurface.withAlpha(15),
              valueColor: const AlwaysStoppedAnimation<Color>(
                MellowColors.brandGreen,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── 学习计划卡片（Drink 风格） ──

  static final _learningTasks = [
    DrinkData('Daily Chat', 100, 'Coffee.png'),
    DrinkData('Vocabulary', 80, 'Latte.png'),
    DrinkData('Grammar', 60, 'Tea.png'),
    DrinkData('Listening', 120, 'Juice.png'),
  ];

  List<Widget> _buildLearningPlanCards() {
    return _learningTasks
        .map(
          (data) => Padding(
            padding: const EdgeInsets.only(bottom: MellowSpacing.sm),
            child: DrinkListCard(
              drinkData: data,
              earnedPoints: 60,
              isOpen: true,
              onTap: (_) {},
            ),
          ),
        )
        .toList();
  }

  // ═══════════════════ 生词本 Tab ═══════════════════

  Widget _buildVocabContent(LearnState state, ThemeData theme) {
    final showShimmer = state.isLoading && state.vocabBook == null && !_isSearching;

    if (showShimmer) {
      return _buildShimmerList();
    }

    // 搜索状态
    if (_isSearching) {
      return Column(
        children: [
          _buildSearchBar(),
          const Expanded(
            child: Center(child: CircularProgressIndicator()),
          ),
        ],
      );
    }

    if (_searchResults.isNotEmpty) {
      return Column(
        children: [
          _buildSearchBar(),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: MellowSpacing.md),
              itemCount: _searchResults.length,
              itemBuilder: (context, index) {
                final word = _searchResults[index];
                return _VocabWordCard(
                  word: word,
                  onTap: () => _showWordDetail(word),
                  onDelete: () => _deleteWord(word),
                );
              },
            ),
          ),
        ],
      );
    }

    // 搜索无结果
    if (_searchController.text.isNotEmpty && _searchResults.isEmpty) {
      return Column(
        children: [
          _buildSearchBar(),
          Expanded(
            child: _buildVocabEmpty(message: '未找到匹配的单词'),
          ),
        ],
      );
    }

    // 错误 + 空数据
    final vocabBook = state.vocabBook;
    final vocabError = state.error;
    if (vocabBook == null) {
      if (vocabError != null) {
        return _buildErrorRetry(
          message: vocabError,
          onRetry: () =>
              ref.read(learnProvider.notifier).fetchVocab(sort: _vocabSort),
        );
      }
      return _buildVocabEmpty();
    }

    final book = vocabBook;
    if (book.groups.isEmpty) {
      return _buildVocabEmpty();
    }

    return Column(
      children: [
        _buildSearchBar(),
        // ── 分组列表 ──
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(
              horizontal: MellowSpacing.md,
            ),
            itemCount: book.groups.length,
            itemBuilder: (context, index) {
              final group = book.groups[index];
              return _VocabGroupSection(
                group: group,
                onTap: _showWordDetail,
                onDelete: _deleteWord,
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        MellowSpacing.md,
        MellowSpacing.md,
        MellowSpacing.md,
        MellowSpacing.sm,
      ),
      child: Row(
        children: [
          Expanded(
            child: ShadInput(
              controller: _searchController,
              placeholder: const Text(MellowStrings.searchWord),
              leading: const Icon(
                LucideIcons.search,
                size: 18,
              ),
              onChanged: (value) {
                _searchDebounce?.cancel();
                if (value.isEmpty) {
                  setState(() {
                    _isSearching = false;
                    _searchResults = [];
                  });
                  ref.read(learnProvider.notifier).fetchVocab(sort: _vocabSort);
                  return;
                }
                _searchDebounce = Timer(const Duration(milliseconds: 300), () {
                  _performSearch(value);
                });
              },
            ),
          ),
          const SizedBox(width: MellowSpacing.sm),
          _SortToggle(
            current: _vocabSort,
            onChanged: _onSortChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildVocabEmpty({String? message}) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(MellowSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            MellowLogo(size: 72, color: MellowColors.border(context)),
            const SizedBox(height: MellowSpacing.lg),
            Text(
              message ?? MellowStrings.noVocabHint,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15,
                color: Theme.of(context)
                    .colorScheme
                    .onSurface
                    .withAlpha(120),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════ 错题 Tab ═══════════════════

  Widget _buildMistakesContent(LearnState state, ThemeData theme) {
    final showShimmer = _mistakesLoading && state.mistakes.isEmpty;

    if (showShimmer) {
      return _buildShimmerList();
    }

    if (state.mistakes.isEmpty) {
      return _buildMistakesEmpty();
    }

    return ListView.separated(
      padding: const EdgeInsets.all(MellowSpacing.md),
      itemCount: state.mistakes.length,
      separatorBuilder: (_, _) =>
          const SizedBox(height: MellowSpacing.sm),
      itemBuilder: (context, index) {
        final mistake = state.mistakes[index];
        return _MistakeCard(
          mistake: mistake,
          theme: theme,
        );
      },
    );
  }

  Widget _buildMistakesEmpty() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(MellowSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              LucideIcons.sparkles,
              size: 56,
              color: MellowColors.brandGreen.withAlpha(80),
            ),
            const SizedBox(height: MellowSpacing.lg),
            Text(
              MellowStrings.noMistakesHint,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15,
                color: Theme.of(context)
                    .colorScheme
                    .onSurface
                    .withAlpha(120),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════ 共享组件 ═══════════════════

  Widget _buildErrorRetry({
    required String message,
    required VoidCallback onRetry,
  }) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            LucideIcons.alertCircle,
            size: 40,
            color: MellowColors.error,
          ),
          const SizedBox(height: MellowSpacing.md),
          Text(
            message,
            style: TextStyle(color: MellowColors.error),
          ),
          const SizedBox(height: MellowSpacing.md),
          ShadButton(
            onPressed: onRetry,
            child: const Text(MellowStrings.retry),
          ),
        ],
      ),
    );
  }

  // ── Shimmer 加载占位 ──

  Widget _buildShimmerProgress() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(MellowSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: List.generate(
              3,
              (_) => Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: _ShimmerBox(
                    height: 88,
                    borderRadius: MellowSpacing.radiusMd,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: MellowSpacing.lg),
          _ShimmerBox(
            height: 44,
            borderRadius: MellowSpacing.radiusMd,
          ),
          const SizedBox(height: MellowSpacing.lg),
          _ShimmerBox(
            height: 140,
            borderRadius: MellowSpacing.radiusLg,
          ),
          const SizedBox(height: MellowSpacing.lg),
          _ShimmerBox(
            height: 40,
            width: 60,
            borderRadius: MellowSpacing.radiusSm,
          ),
          const SizedBox(height: MellowSpacing.sm),
          ...List.generate(
            3,
            (_) => Padding(
              padding: const EdgeInsets.only(bottom: MellowSpacing.sm),
              child: _ShimmerBox(
                height: 36,
                borderRadius: MellowSpacing.radiusSm,
              ),
            ),
          ),
          const SizedBox(height: MellowSpacing.lg),
          _ShimmerBox(
            height: 100,
            borderRadius: MellowSpacing.radiusLg,
          ),
          const SizedBox(height: MellowSpacing.lg),
          _ShimmerBox(
            height: 48,
            borderRadius: MellowSpacing.radiusMd,
          ),
        ],
      ),
    );
  }

  Widget _buildShimmerList() {
    return ListView.separated(
      padding: const EdgeInsets.all(MellowSpacing.md),
      itemCount: 8,
      separatorBuilder: (_, _) =>
          const SizedBox(height: MellowSpacing.sm),
      itemBuilder: (context, index) {
        return _ShimmerBox(
          height: 64,
          borderRadius: MellowSpacing.radiusMd,
        );
      },
    );
  }
}

// ═══════════════════ 统计卡片 ═══════════════════

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color iconColor;

  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ShadCard(
      padding: const EdgeInsets.all(MellowSpacing.md),
      backgroundColor: theme.colorScheme.surface,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: iconColor.withAlpha(25),
              borderRadius:
                  BorderRadius.circular(MellowSpacing.radiusSm),
            ),
            alignment: Alignment.center,
            child: Icon(icon, size: 18, color: iconColor),
          ),
          const SizedBox(height: MellowSpacing.sm),
          Text(
            value,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withAlpha(130),
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════ 区块标题 ═══════════════════

class _SectionTitle extends StatelessWidget {
  final String title;

  const _SectionTitle({required this.title});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Text(
      title,
      style: theme.textTheme.titleSmall?.copyWith(
        fontWeight: FontWeight.w600,
      ),
    );
  }
}

// ═══════════════════ 排序切换按钮 ═══════════════════

class _SortToggle extends StatelessWidget {
  final String current;
  final ValueChanged<String> onChanged;

  const _SortToggle({
    required this.current,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final options = [
      ('recent', MellowStrings.recent),
      ('alpha', MellowStrings.alpha),
    ];

    return Container(
      height: 42,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(MellowSpacing.radiusSm),
        border: Border.all(
          color: MellowColors.border(context).withAlpha(120),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: options.map((opt) {
          final selected = current == opt.$1;
          return GestureDetector(
            onTap: () => onChanged(opt.$1),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: selected ? MellowColors.brandGreen : null,
                borderRadius: BorderRadius.circular(
                  MellowSpacing.radiusSm,
                ),
              ),
              child: Text(
                opt.$2,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight:
                      selected ? FontWeight.w600 : FontWeight.w400,
                  color: selected
                      ? Colors.white
                      : theme.colorScheme.onSurface.withAlpha(160),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

// ═══════════════════ 生词本分组区块 ═══════════════════

class _VocabGroupSection extends StatelessWidget {
  final VocabGroup group;
  final void Function(WordEntry word) onTap;
  final Future<void> Function(WordEntry word) onDelete;

  const _VocabGroupSection({
    required this.group,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // 分组头部（首字母）
        Padding(
          padding: const EdgeInsets.only(
            top: MellowSpacing.md,
            bottom: MellowSpacing.sm,
          ),
          child: Row(
            children: [
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: MellowColors.brandGreen.withAlpha(30),
                  borderRadius: BorderRadius.circular(6),
                ),
                alignment: Alignment.center,
                child: Text(
                  group.letter.toUpperCase(),
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: MellowColors.brandGreen,
                  ),
                ),
              ),
              const SizedBox(width: MellowSpacing.sm),
              Text(
                MellowStrings.wordCount(group.count),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurface.withAlpha(120),
                ),
              ),
            ],
          ),
        ),

        // 单词卡片列表
        ...group.words.map(
          (word) => _VocabWordCard(
            word: word,
            onTap: () => onTap(word),
            onDelete: () => onDelete(word),
          ),
        ),
      ],
    );
  }
}

// ═══════════════════ 生词卡片 ═══════════════════

class _VocabWordCard extends StatelessWidget {
  final WordEntry word;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _VocabWordCard({
    required this.word,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defPreview = word.definitions.isNotEmpty
        ? word.definitions.first
        : MellowStrings.noDefinition;

    return Dismissible(
      key: ValueKey('vocab_${word.word}'),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: MellowSpacing.lg),
        decoration: BoxDecoration(
          color: MellowColors.error,
          borderRadius: BorderRadius.circular(MellowSpacing.radiusMd),
        ),
        child: const Icon(
          LucideIcons.trash2,
          color: Colors.white,
          size: 20,
        ),
      ),
      confirmDismiss: (_) async {
        onDelete();
        // 不等待 API，直接关闭
        return false;
      },
      child: GestureDetector(
        onTap: onTap,
        child: ShadCard(
          padding: const EdgeInsets.symmetric(
            horizontal: MellowSpacing.md,
            vertical: MellowSpacing.sm + 2,
          ),
          backgroundColor: theme.colorScheme.surface,
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      word.word,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (defPreview.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        defPreview,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurface
                              .withAlpha(130),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              Icon(
                LucideIcons.chevronRight,
                size: 18,
                color: theme.colorScheme.onSurface.withAlpha(80),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ═══════════════════ 单词详情弹出层 ═══════════════════

class _WordDetailSheet extends StatelessWidget {
  final WordEntry word;
  final ThemeData theme;

  const _WordDetailSheet({
    required this.word,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        MellowSpacing.lg,
        MellowSpacing.md,
        MellowSpacing.lg,
        MellowSpacing.xl,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: theme.colorScheme.onSurface.withAlpha(40),
                borderRadius:
                    BorderRadius.circular(MellowSpacing.radiusFull),
              ),
            ),
          ),
          const SizedBox(height: MellowSpacing.lg),

          // 单词 + 音标
          Row(
            children: [
              Expanded(
                child: Text(
                  word.word,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              Builder(builder: (context) {
                final pos = word.partOfSpeech;
                if (pos != null) {
                  return ShadBadge(
                    child: Text(
                      pos,
                      style: const TextStyle(fontSize: 12),
                    ),
                  );
                }
                return const SizedBox.shrink();
              }),
            ],
          ),
          Builder(builder: (context) {
            final phonetic = word.phonetic;
            if (phonetic != null) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: MellowSpacing.xs),
                  Text(
                    phonetic,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface.withAlpha(130),
                    ),
                  ),
                ],
              );
            }
            return const SizedBox.shrink();
          }),
          const SizedBox(height: MellowSpacing.lg),

          // 释义
          if (word.definitions.isNotEmpty) ...[
            _DetailSectionTitle(title: MellowStrings.definitions),
            const SizedBox(height: MellowSpacing.xs),
            ...word.definitions.map(
              (d) => Padding(
                padding: const EdgeInsets.only(
                  bottom: MellowSpacing.xs,
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '• ',
                      style: TextStyle(
                        color: MellowColors.brandGreen,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        d,
                        style: theme.textTheme.bodyMedium,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: MellowSpacing.md),
          ],

          // 例句
          if (word.examples.isNotEmpty) ...[
            _DetailSectionTitle(title: MellowStrings.examples),
            const SizedBox(height: MellowSpacing.xs),
            ...word.examples.map(
              (e) => Padding(
                padding: const EdgeInsets.only(
                  bottom: MellowSpacing.sm,
                ),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(MellowSpacing.sm + 2),
                  decoration: BoxDecoration(
                    color:
                        MellowColors.brandGreen.withAlpha(12),
                    borderRadius: BorderRadius.circular(
                      MellowSpacing.radiusSm,
                    ),
                  ),
                  child: Text(
                    e,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontStyle: FontStyle.italic,
                      color: theme.colorScheme.onSurface
                          .withAlpha(200),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: MellowSpacing.md),
          ],

          // 近义词
          if (word.synonyms.isNotEmpty) ...[
            _DetailSectionTitle(title: MellowStrings.synonyms),
            const SizedBox(height: MellowSpacing.xs),
            Wrap(
              spacing: MellowSpacing.xs,
              runSpacing: MellowSpacing.xs,
              children: word.synonyms
                  .map(
                    (s) => Chip(
                      materialTapTargetSize:
                          MaterialTapTargetSize.shrinkWrap,
                      visualDensity: VisualDensity.compact,
                      label: Text(s, style: const TextStyle(fontSize: 13)),
                      backgroundColor:
                          MellowColors.brandOrange.withAlpha(20),
                      side: BorderSide.none,
                    ),
                  )
                  .toList(),
            ),
          ],
        ],
      ),
    );
  }
}

class _DetailSectionTitle extends StatelessWidget {
  final String title;

  const _DetailSectionTitle({required this.title});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Text(
      title,
      style: theme.textTheme.labelMedium?.copyWith(
        fontWeight: FontWeight.w600,
        color: MellowColors.brandGreen,
      ),
    );
  }
}

// ═══════════════════ 错题卡片 ═══════════════════

class _MistakeCard extends StatelessWidget {
  final Mistake mistake;
  final ThemeData theme;

  const _MistakeCard({
    required this.mistake,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return ShadCard(
      padding: const EdgeInsets.all(MellowSpacing.md),
      backgroundColor: theme.colorScheme.surface,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 错误类型徽章
          Row(
            children: [
              ShadBadge(
                backgroundColor: MellowColors.brandOrange.withAlpha(30),
                foregroundColor: MellowColors.brandOrange,
                child: Text(
                  mistake.mistakeType,
                  style: const TextStyle(fontSize: 12),
                ),
              ),
              const Spacer(),
              if (mistake.timestamp.isNotEmpty)
                Text(
                  _formatDate(mistake.timestamp),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withAlpha(100),
                    fontSize: 12,
                  ),
                ),
            ],
          ),
          const SizedBox(height: MellowSpacing.sm),

          // 错误 → 正确
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: MellowColors.error.withAlpha(15),
                    borderRadius: BorderRadius.circular(
                      MellowSpacing.radiusSm,
                    ),
                  ),
                  child: Text(
                    mistake.wordOrRule,
                    style: TextStyle(
                      color: MellowColors.error,
                      fontWeight: FontWeight.w500,
                      decoration: TextDecoration.lineThrough,
                    ),
                  ),
                ),
              ),
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 8),
                child: Icon(
                  LucideIcons.arrowRight,
                  size: 18,
                  color: MellowColors.brandGreen,
                ),
              ),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: MellowColors.brandGreen.withAlpha(15),
                    borderRadius: BorderRadius.circular(
                      MellowSpacing.radiusSm,
                    ),
                  ),
                  child: Text(
                    mistake.correction,
                    style: const TextStyle(
                      color: MellowColors.brandGreen,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
            ],
          ),

          // 上下文
          if (mistake.context.isNotEmpty) ...[
            const SizedBox(height: MellowSpacing.sm),
            Text(
              mistake.context,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withAlpha(110),
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _formatDate(String iso) {
    try {
      final dt = DateTime.parse(iso);
      return '${dt.month}/${dt.day}';
    } catch (_) {
      return '';
    }
  }
}

// ═══════════════════ Shimmer 动画 ═══════════════════

class _ShimmerBox extends StatefulWidget {
  final double? width;
  final double height;
  final double borderRadius;

  const _ShimmerBox({
    this.width,
    required this.height,
    this.borderRadius = 8,
  });

  @override
  State<_ShimmerBox> createState() => _ShimmerBoxState();
}

class _ShimmerBoxState extends State<_ShimmerBox>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Color _baseColor(Brightness brightness) {
    return brightness == Brightness.dark
        ? const Color(0xFF21262D)
        : const Color(0xFFE5E7EB);
  }

  Color _highlightColor(Brightness brightness) {
    return brightness == Brightness.dark
        ? const Color(0xFF30363D)
        : const Color(0xFFF3F4F6);
  }

  @override
  Widget build(BuildContext context) {
    final brightness = Theme.of(context).brightness;

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius:
                BorderRadius.circular(widget.borderRadius),
            gradient: LinearGradient(
              begin: Alignment(
                -1.0 + _controller.value * 2,
                0,
              ),
              end: Alignment(
                1.0 + _controller.value * 2,
                0,
              ),
              colors: [
                _baseColor(brightness),
                _highlightColor(brightness),
                _baseColor(brightness),
              ],
            ),
          ),
        );
      },
    );
  }
}
