import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../providers/auth_provider.dart';
import '../../shared/constants/ui_strings.dart';
import '../../shared/constants/validation_errors.dart';
import '../../shared/widgets/mellow_logo.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirm = true;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    await ref.read(authProvider.notifier).register(
          _usernameController.text.trim(),
          _passwordController.text,
        );

    if (!mounted) return;

    final authState = ref.read(authProvider);
    if (authState.status == AuthStatus.authenticated) {
      context.go('/personas');
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: MellowSpacing.lg),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Logo
                  const MellowLogo(size: 80),
                  const SizedBox(height: MellowSpacing.md),
                  Text(
                    MellowStrings.createAccount,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.headlineLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: MellowSpacing.xs),
                  Text(
                    MellowStrings.joinMellow,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: MellowColors.textSecondary(context),
                    ),
                  ),
                  const SizedBox(height: MellowSpacing.xl),

                  // 错误提示
                  if (authState.error case final error?) ...[
                    Container(
                      padding: const EdgeInsets.all(MellowSpacing.sm),
                      decoration: BoxDecoration(
                        color: MellowColors.error.withAlpha(25),
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusSm),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline,
                              color: MellowColors.error, size: 18),
                          const SizedBox(width: MellowSpacing.sm),
                          Expanded(
                            child: Text(
                              error,
                              style: const TextStyle(
                                  color: MellowColors.error, fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: MellowSpacing.md),
                  ],

                  // 用户名
                  TextFormField(
                    controller: _usernameController,
                    decoration: InputDecoration(
                      labelText: MellowStrings.username,
                      hintText: MellowStrings.usernameHint,
                      prefixIcon: const Icon(Icons.person_outline),
                      border: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                        borderSide:
                            BorderSide(color: MellowColors.border(context)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                        borderSide: const BorderSide(
                            color: MellowColors.brandGreen, width: 2),
                      ),
                    ),
                    validator: (v) {
                      if (v == null || v.trim().length < 3) {
                        return MellowValidationErrors.usernameTooShort;
                      }
                      return null;
                    },
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: MellowSpacing.md),

                  // 密码
                  TextFormField(
                    controller: _passwordController,
                    obscureText: _obscurePassword,
                    decoration: InputDecoration(
                      labelText: MellowStrings.password,
                      hintText: MellowStrings.passwordHint,
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(_obscurePassword
                            ? Icons.visibility_off
                            : Icons.visibility),
                        onPressed: () {
                          setState(() => _obscurePassword = !_obscurePassword);
                        },
                      ),
                      border: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                        borderSide:
                            BorderSide(color: MellowColors.border(context)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                        borderSide: const BorderSide(
                            color: MellowColors.brandGreen, width: 2),
                      ),
                    ),
                    validator: (v) {
                      if (v == null || v.length < 6) {
                        return MellowValidationErrors.passwordTooShort;
                      }
                      return null;
                    },
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: MellowSpacing.md),

                  // 确认密码
                  TextFormField(
                    controller: _confirmPasswordController,
                    obscureText: _obscureConfirm,
                    decoration: InputDecoration(
                      labelText: MellowStrings.confirmPassword,
                      hintText: MellowStrings.confirmPasswordHint,
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(_obscureConfirm
                            ? Icons.visibility_off
                            : Icons.visibility),
                        onPressed: () {
                          setState(() => _obscureConfirm = !_obscureConfirm);
                        },
                      ),
                      border: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                        borderSide:
                            BorderSide(color: MellowColors.border(context)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(MellowSpacing.radiusMd),
                        borderSide: const BorderSide(
                            color: MellowColors.brandGreen, width: 2),
                      ),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) {
                        return MellowValidationErrors.confirmRequired;
                      }
                      if (v != _passwordController.text) {
                        return MellowValidationErrors.passwordMismatch;
                      }
                      return null;
                    },
                    textInputAction: TextInputAction.done,
                    onFieldSubmitted: (_) => _handleRegister(),
                  ),
                  const SizedBox(height: MellowSpacing.lg),

                  // 注册按钮
                  SizedBox(
                    height: 48,
                    child: ElevatedButton(
                      onPressed: authState.isLoading ? null : _handleRegister,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: MellowColors.brandGreen,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius:
                              BorderRadius.circular(MellowSpacing.radiusMd),
                        ),
                        elevation: 0,
                      ),
                      child: authState.isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                           : const Text(
                               MellowStrings.register,
                              style: TextStyle(
                                  fontSize: 16, fontWeight: FontWeight.w600),
                            ),
                    ),
                  ),
                  const SizedBox(height: MellowSpacing.md),

                  // 登录入口
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        MellowStrings.hasAccount,
                        style: TextStyle(color: MellowColors.textSecondary(context)),
                      ),
                      TextButton(
                        onPressed: () => context.go('/auth/login'),
                        style: TextButton.styleFrom(
                          foregroundColor: MellowColors.brandGreen,
                        ),
                        child: const Text(MellowStrings.loginNow),
                      ),
                    ],
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
