import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';

import '../features/splash/splash_screen.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';
import '../features/personas/persona_select_screen.dart';
import '../features/personas/persona_detail_screen.dart';
import '../features/chat/chat_screen.dart';
import '../features/learn/learn_screen.dart';
import '../features/profile/profile_screen.dart';
import '../shared/vignettes/bubble_tab_bar/navbar.dart';
import '../theme/colors.dart';

final _rootKey = GlobalKey<NavigatorState>();
// _shellKey not needed for StatefulShellRoute

GoRouter createAppRouter() => GoRouter(
      navigatorKey: _rootKey,
      initialLocation: '/splash',
      routes: [
        GoRoute(
          path: '/splash',
          builder: (context, state) => const SplashScreen(),
        ),
        GoRoute(
          path: '/auth/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/auth/register',
          builder: (context, state) => const RegisterScreen(),
        ),
        StatefulShellRoute.indexedStack(
          builder: (context, state, navigationShell) {
            return MainShell(navigationShell: navigationShell);
          },
          branches: [
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/chat',
                  builder: (context, state) => const ChatScreen(),
                ),
              ],
            ),
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/learn',
                  builder: (context, state) => const LearnScreen(),
                ),
              ],
            ),
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/profile',
                  builder: (context, state) => const ProfileScreen(),
                ),
              ],
            ),
          ],
        ),
        GoRoute(
          path: '/personas',
          builder: (context, state) => const PersonaSelectScreen(),
        ),
        GoRoute(
          path: '/personas/:id',
          builder: (context, state) {
            final id = state.pathParameters['id']!;
            return PersonaDetailScreen(personaId: id);
          },
        ),
      ],
    );

/// 主壳层 — 包含 bubble_tab_bar 底部导航
class MainShell extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const MainShell({super.key, required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavBar(
        items: [
          NavBarItemData('Chat', Icons.chat, 100.0, MellowColors.brandGreen),
          NavBarItemData('Learn', Icons.school, 100.0, MellowColors.brandGreen),
          NavBarItemData('Profile', Icons.person, 100.0, MellowColors.brandGreen),
        ],
        currentIndex: navigationShell.currentIndex,
        itemTapped: (index) => navigationShell.goBranch(index),
      ),
    );
  }
}
