import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import 'providers/theme_provider.dart';
import 'router/app_router.dart';
import 'theme/shadcn_theme.dart';

void main() {
  runApp(const ProviderScope(child: MellowApp()));
}

final _router = createAppRouter();

class MellowApp extends ConsumerWidget {
  const MellowApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);

    return ScaffoldMessenger(
      child: ShadApp.router(
        key: ValueKey(themeMode),
        theme: mellowLightTheme,
        darkTheme: mellowDarkTheme,
        themeMode: themeMode,
        routerConfig: _router,
        debugShowCheckedModeBanner: false,
        title: 'Mellow',
      ),
    );
  }
}
