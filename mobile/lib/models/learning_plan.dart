class DailyPlan {
  final int day;
  final String topic;
  final List<String> vocabulary;
  final String grammarPoint;
  final String practice;

  DailyPlan({
    required this.day,
    this.topic = '',
    this.vocabulary = const [],
    this.grammarPoint = '',
    this.practice = '',
  });

  factory DailyPlan.fromJson(Map<String, dynamic> json) => DailyPlan(
        day: json['day'] ?? 0,
        topic: json['topic'] ?? '',
        vocabulary: List<String>.from(json['vocabulary'] ?? []),
        grammarPoint: json['grammar_point'] ?? '',
        practice: json['practice'] ?? '',
      );
}

class WeeklyPlan {
  final int week;
  final String theme;
  final List<DailyPlan> days;
  final bool completed;

  WeeklyPlan({
    required this.week,
    this.theme = '',
    this.days = const [],
    this.completed = false,
  });

  factory WeeklyPlan.fromJson(Map<String, dynamic> json) => WeeklyPlan(
        week: json['week'] ?? 0,
        theme: json['theme'] ?? '',
        days: (json['days'] as List<dynamic>?)
                ?.map((d) => DailyPlan.fromJson(d))
                .toList() ??
            [],
        completed: json['completed'] ?? false,
      );
}
