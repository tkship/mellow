import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _user = TextEditingController();
  final _pass = TextEditingController();
  var _reg = false;
  String? _err;
  var _loading = false;

  @override
  void dispose() { _user.dispose(); _pass.dispose(); super.dispose(); }

  Future<void> _submit() async {
    final u = _user.text.trim(); final p = _pass.text.trim();
    if (u.isEmpty || p.isEmpty) { setState(() => _err = '请填写用户名和密码'); return; }
    setState(() { _err = null; _loading = true; });
    final e = _reg ? await context.read<AuthProvider>().register(u, p) : await context.read<AuthProvider>().login(u, p);
    if (!mounted) return;
    if (e != null) setState(() { _err = e; _loading = false; });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Scaffold(
      body: Stack(
        children: [
          // ── Background blob ──
          Positioned(
            top: -120, right: -80,
            child: Container(
              width: 320, height: 320,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(colors: [cs.primaryContainer.withAlpha(160), Colors.transparent]),
              ),
            ),
          ),
          Positioned(
            bottom: -60, left: -40,
            child: Container(
              width: 200, height: 200,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(colors: [cs.secondaryContainer.withAlpha(120), Colors.transparent]),
              ),
            ),
          ),
          // ── Content ──
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const SizedBox(height: 48),
                    // Logo
                    Container(
                      width: 88, height: 88,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [Color(0xFFFF7B6C), Color(0xFFFF9E95)]),
                        borderRadius: BorderRadius.circular(26),
                        boxShadow: [BoxShadow(color: cs.primary.withAlpha(50), blurRadius: 20, offset: const Offset(0, 8))],
                      ),
                      child: const Center(child: Text('M', style: TextStyle(color: Colors.white, fontSize: 44, fontWeight: FontWeight.w800))),
                    ),
                    const SizedBox(height: 28),
                    Text('Mellow', style: theme.textTheme.headlineLarge?.copyWith(fontWeight: FontWeight.w800, color: cs.primary)),
                    const SizedBox(height: 6),
                    Text(_reg ? '创建账号，开始学习' : '你的AI英语学习伙伴', style: theme.textTheme.bodyMedium?.copyWith(color: cs.outline)),
                    const SizedBox(height: 48),
                    // Toggle pill
                    Container(
                      decoration: BoxDecoration(color: cs.surfaceContainerHighest, borderRadius: BorderRadius.circular(28)),
                      child: Row(children: [
                        _pill('登录', !_reg, () => setState(() => _reg = false), cs),
                        _pill('注册', _reg, () => setState(() => _reg = true), cs),
                      ]),
                    ),
                    const SizedBox(height: 28),
                    // Username
                    TextField(
                      controller: _user,
                      decoration: InputDecoration(
                        hintText: '用户名',
                        prefixIcon: const Icon(Icons.person_outline, size: 22),
                        filled: true, fillColor: cs.surfaceContainerHighest.withAlpha(120),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                      ),
                    ),
                    const SizedBox(height: 14),
                    // Password
                    TextField(
                      controller: _pass, obscureText: true,
                      decoration: InputDecoration(
                        hintText: '密码',
                        prefixIcon: const Icon(Icons.lock_outline, size: 22),
                        filled: true, fillColor: cs.surfaceContainerHighest.withAlpha(120),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                      ),
                      onSubmitted: (_) => _submit(),
                    ),
                    if (_err != null) ...[
                      const SizedBox(height: 14),
                      Container(
                        width: double.infinity, padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(color: cs.errorContainer, borderRadius: BorderRadius.circular(14)),
                        child: Row(children: [
                          Icon(Icons.error_outline, color: cs.error, size: 18),
                          const SizedBox(width: 10),
                          Expanded(child: Text(_err!, style: TextStyle(color: cs.error, fontSize: 13))),
                        ]),
                      ),
                    ],
                    const SizedBox(height: 28),
                    // Submit button
                    Container(
                      width: double.infinity, height: 56,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(colors: [cs.primary, cs.tertiary]),
                        borderRadius: BorderRadius.circular(28),
                        boxShadow: [BoxShadow(color: cs.primary.withAlpha(40), blurRadius: 12, offset: const Offset(0, 4))],
                      ),
                      child: Material(
                        color: Colors.transparent,
                        child: InkWell(
                          borderRadius: BorderRadius.circular(28),
                          onTap: _loading ? null : _submit,
                          child: Center(
                            child: _loading
                                ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white))
                                : Text(_reg ? '创建账号' : '登录', style: const TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.w700)),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 60),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _pill(String label, bool active, VoidCallback tap, ColorScheme cs) {
    return Expanded(
      child: GestureDetector(
        onTap: tap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          padding: const EdgeInsets.symmetric(vertical: 13),
          decoration: BoxDecoration(
            color: active ? cs.primary : Colors.transparent,
            borderRadius: BorderRadius.circular(28),
          ),
          child: Center(child: Text(label, style: TextStyle(color: active ? cs.onPrimary : cs.outline, fontWeight: FontWeight.w700))),
        ),
      ),
    );
  }
}
