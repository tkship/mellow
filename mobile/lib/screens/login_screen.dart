import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with SingleTickerProviderStateMixin {
  final _usernameCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _isRegister = false;

  late final AnimationController _pulseCtrl;
  late final Animation<double> _pulseScale;
  late final Animation<double> _pulseOpacity;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );
    _pulseScale = Tween<double>(begin: 1.0, end: 1.12).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );
    _pulseOpacity = Tween<double>(begin: 0.4, end: 0.08).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );
    _pulseCtrl.repeat(reverse: true);
  }

  @override
  void dispose() {
    _usernameCtrl.dispose();
    _passwordCtrl.dispose();
    _pulseCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final auth = context.read<AuthProvider>();
    final username = _usernameCtrl.text.trim();
    final password = _passwordCtrl.text.trim();

    if (username.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('请输入用户名')),
        );
      }
      return;
    }
    if (password.length < 6) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('密码长度至少为 6 个字符')),
        );
      }
      return;
    }

    String? error;
    try {
      if (_isRegister) {
        error = await auth.register(username, password);
        if (error == null && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('注册成功！欢迎加入 Mellow 🎉'),
              backgroundColor: Colors.teal,
            ),
          );
        }
      } else {
        error = await auth.login(username, password);
      }
    } catch (e) {
      error = '操作失败：$e';
    }

    if (error != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      body: Stack(
        children: [
          // Layer 1a: Deep solid base
          Container(color: theme.colorScheme.surface),
          // Layer 1b: Radial focal glow (top-center emphasis)
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(0, -0.45),
                  radius: 1.3,
                  colors: [
                    theme.colorScheme.primaryContainer.withOpacity(0.55),
                    theme.colorScheme.secondaryContainer.withOpacity(0.20),
                    theme.colorScheme.surface.withOpacity(0.0),
                  ],
                ),
              ),
            ),
          ),
          // Layer 1c: Warm gradient wash from bottom
          Positioned.fill(
            child: Align(
              alignment: Alignment.bottomCenter,
              child: IgnorePointer(
                child: Container(
                  height: MediaQuery.of(context).size.height * 0.45,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.bottomCenter,
                      end: Alignment.topCenter,
                      colors: [
                        theme.colorScheme.tertiaryContainer.withOpacity(0.22),
                        theme.colorScheme.primaryContainer.withOpacity(0.08),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          // Layer 2: Floating particles
          const _ParticleField(),
          // Layer 3: Main content
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(32, 60, 32, 32),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildBrandHeader(theme),
                    const SizedBox(height: 40),
                    _buildFormCard(theme, auth),
                    const SizedBox(height: 24),
                    _buildToggleLink(theme),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBrandHeader(ThemeData theme) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Animated icon inside a pulsing glow ring
        AnimatedBuilder(
          animation: _pulseCtrl,
          builder: (_, child) => Stack(
            alignment: Alignment.center,
            children: [
              // Outer slow glow ring
              Transform.scale(
                scale: 1.0 + (_pulseScale.value - 1.0) * 1.4,
                child: Opacity(
                  opacity: _pulseOpacity.value * 0.6,
                  child: Container(
                    width: 88,
                    height: 88,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: theme.colorScheme.primary.withOpacity(0.25),
                        width: 2,
                      ),
                    ),
                  ),
                ),
              ),
              // Inner glow ring
              Transform.scale(
                scale: _pulseScale.value,
                child: Opacity(
                  opacity: _pulseOpacity.value,
                  child: Container(
                    width: 88,
                    height: 88,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: theme.colorScheme.primary.withOpacity(0.5),
                        width: 3,
                      ),
                    ),
                  ),
                ),
              ),
              // Icon circle
              Container(
                width: 88,
                height: 88,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      theme.colorScheme.primaryContainer,
                      theme.colorScheme.secondaryContainer,
                    ],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: theme.colorScheme.primary.withOpacity(0.35),
                      blurRadius: 24,
                      offset: const Offset(0, 8),
                    ),
                    BoxShadow(
                      color: theme.colorScheme.tertiary.withOpacity(0.15),
                      blurRadius: 40,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Icon(
                  Icons.auto_awesome,
                  size: 40,
                  color: theme.colorScheme.primary,
                ),
              ),
            ],
          ),
        ).animate().fadeIn(duration: 600.ms).scale(
              begin: const Offset(0.8, 0.8),
            ),
        const SizedBox(height: 24),
        // App title
        ShaderMask(
          shaderCallback: (bounds) => LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              theme.colorScheme.primary,
              theme.colorScheme.tertiary,
            ],
          ).createShader(bounds),
          child: Text(
            'Mellow',
            style: theme.textTheme.headlineLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ).animate().fadeIn(delay: 200.ms).slideY(begin: 10),
        const SizedBox(height: 10),
        // Decorative accent dot
        Container(
          width: 6,
          height: 6,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: theme.colorScheme.primary.withOpacity(0.5),
                blurRadius: 8,
                spreadRadius: 1,
              ),
            ],
          ),
        ).animate().fadeIn(delay: 350.ms).scale(
              begin: const Offset(0, 0),
              curve: Curves.elasticOut,
            ),
        const SizedBox(height: 6),
        // Subtitle with crossfade
        AnimatedSwitcher(
          duration: 300.ms,
          child: Text(
            _isRegister ? '创建你的学习账号' : '欢迎回来，继续学习',
            key: ValueKey(_isRegister),
            style: theme.textTheme.bodyLarge?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ).animate().fadeIn(delay: 400.ms),
      ],
    );
  }

  Widget _buildFormCard(ThemeData theme, AuthProvider auth) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(22),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            theme.colorScheme.primary.withOpacity(_isRegister ? 0.15 : 0.2),
            theme.colorScheme.tertiary.withOpacity(_isRegister ? 0.08 : 0.10),
            theme.colorScheme.secondary.withOpacity(0.06),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: theme.colorScheme.primary.withOpacity(0.12),
            blurRadius: 30,
            offset: const Offset(0, 12),
          ),
          BoxShadow(
            color: theme.colorScheme.tertiary.withOpacity(0.06),
            blurRadius: 60,
            offset: const Offset(0, 24),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: BackdropFilter(
          filter: ui.ImageFilter.blur(sigmaX: 12, sigmaY: 12),
          child: Card(
            elevation: 0,
            shadowColor: Colors.transparent,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            color: theme.colorScheme.surface.withOpacity(0.86),
            margin: const EdgeInsets.all(2), // gap for gradient border
            child: Column(
              mainAxisSize: MainAxisSize.min,
            children: [
              // Gradient color strip
              Container(
                height: 4,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: _isRegister
                        ? [Colors.teal, Colors.tealAccent.shade200]
                        : [
                            theme.colorScheme.primary,
                            theme.colorScheme.tertiary,
                          ],
                  ),
                  borderRadius:
                      const BorderRadius.vertical(top: Radius.circular(20)),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Username field — slides in from left
                    TextField(
                      controller: _usernameCtrl,
                      textInputAction: TextInputAction.next,
                      decoration: InputDecoration(
                        labelText: '用户名',
                        prefixIcon: Icon(Icons.person,
                            color: theme.colorScheme.primary),
                        filled: true,
                        fillColor: theme.colorScheme.surfaceContainerHighest,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide.none,
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide.none,
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide(
                            color: theme.colorScheme.primary,
                            width: 2,
                          ),
                        ),
                      ),
                    )
                        .animate()
                        .fadeIn(delay: 500.ms, duration: 400.ms)
                        .slideX(begin: -20),
                    const SizedBox(height: 16),
                    // Password field — slides in from right
                    TextField(
                      controller: _passwordCtrl,
                      obscureText: true,
                      textInputAction: TextInputAction.done,
                      onSubmitted: auth.loading ? null : (_) => _submit(),
                      decoration: InputDecoration(
                        labelText: '密码',
                        prefixIcon: Icon(Icons.lock,
                            color: theme.colorScheme.primary),
                        filled: true,
                        fillColor: theme.colorScheme.surfaceContainerHighest,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide.none,
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide.none,
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide(
                            color: theme.colorScheme.primary,
                            width: 2,
                          ),
                        ),
                      ),
                    )
                        .animate()
                        .fadeIn(delay: 650.ms, duration: 400.ms)
                        .slideX(begin: 20),
                    const SizedBox(height: 24),
                    // Submit button — bounce on press
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: _BouncyButton(
                        onPressed: auth.loading ? null : _submit,
                        color: theme.colorScheme.primary,
                        child: auth.loading
                            ? SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: theme.colorScheme.onPrimary,
                                ),
                              )
                            : Text(
                                _isRegister ? '注册' : '登录',
                                style: theme.textTheme.labelLarge,
                              ),
                      ),
                    ).animate().fadeIn(delay: 800.ms).slideY(begin: 10),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      ),
    );
  }

  Widget _buildToggleLink(ThemeData theme) {
    return TextButton(
      onPressed: () => setState(() => _isRegister = !_isRegister),
      child: AnimatedSwitcher(
        duration: 300.ms,
        child: Text(
          _isRegister ? '已有账号？去登录' : '没有账号？去注册',
          key: ValueKey(_isRegister),
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.primary,
          ),
        ),
      ),
    );
  }
}

// ─── Bouncy button wrapper ──────────────────────────────────────────
class _BouncyButton extends StatefulWidget {
  final VoidCallback? onPressed;
  final Widget child;
  final Color color;
  const _BouncyButton({
    required this.onPressed,
    required this.child,
    required this.color,
  });

  @override
  State<_BouncyButton> createState() => _BouncyButtonState();
}

class _BouncyButtonState extends State<_BouncyButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _scale = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 0.95), weight: 1),
      TweenSequenceItem(
          tween: Tween(begin: 0.95, end: 1.0), weight: 2),
    ]).animate(_ctrl);
    _ctrl.addStatusListener((s) {
      if (s == AnimationStatus.completed) _ctrl.reset();
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  void _onTap() {
    if (widget.onPressed != null) {
      _ctrl.forward(from: 0.0);
      widget.onPressed!();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _scale,
      builder: (_, child) => Transform.scale(scale: _scale.value, child: child),
      child: FilledButton(
        style: FilledButton.styleFrom(shape: const StadiumBorder()),
        onPressed: widget.onPressed == null ? null : _onTap,
        child: widget.child,
      ),
    );
  }
}

// ─── Floating particle field ────────────────────────────────────────
class _ParticleField extends StatefulWidget {
  const _ParticleField();

  @override
  State<_ParticleField> createState() => _ParticleFieldState();
}

class _ParticleFieldState extends State<_ParticleField>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  final _random = Random(42);
  final _particles = <_Particle>[];

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 20),
    );
    // Create 12 floating shapes of mixed types
    for (int i = 0; i < 12; i++) {
      _particles.add(_Particle(
        size: 6.0 + _random.nextDouble() * 18,
        x: _random.nextDouble(),
        y: _random.nextDouble(),
        speedX: 0.15 + _random.nextDouble() * 0.7,
        speedY: 0.15 + _random.nextDouble() * 0.7,
        opacity: 0.04 + _random.nextDouble() * 0.12,
        shape: i % 3 == 0
            ? _ParticleShape.diamond
            : (i % 3 == 1 ? _ParticleShape.circle : _ParticleShape.square),
        rotation: _random.nextDouble() * 3.14 * 2,
        rotationSpeed: (_random.nextDouble() - 0.5) * 0.4,
      ));
    }
    _ctrl.repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, __) => CustomPaint(
        size: Size.infinite,
        painter: _ParticlePainter(
          particles: _particles,
          color: cs.primary,
          time: _ctrl.value,
        ),
      ),
    );
  }
}

enum _ParticleShape { circle, diamond, square }

class _Particle {
  final double size;
  final double x, y;
  final double speedX, speedY;
  final double opacity;
  final _ParticleShape shape;
  final double rotation;
  final double rotationSpeed;
  _Particle({
    required this.size,
    required this.x,
    required this.y,
    required this.speedX,
    required this.speedY,
    required this.opacity,
    this.shape = _ParticleShape.circle,
    this.rotation = 0,
    this.rotationSpeed = 0,
  });
}

class _ParticlePainter extends CustomPainter {
  final List<_Particle> particles;
  final Color color;
  final double time;

  _ParticlePainter({
    required this.particles,
    required this.color,
    required this.time,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (final p in particles) {
      final dx = ((p.x + time * p.speedX) % 1.0) * size.width;
      final dy = ((p.y + time * p.speedY) % 1.0) * size.height;
      final paint = Paint()
        ..color = color.withOpacity(p.opacity)
        ..style = PaintingStyle.fill;
      canvas.save();
      canvas.translate(dx, dy);
      canvas.rotate(p.rotation + time * p.rotationSpeed);

      switch (p.shape) {
        case _ParticleShape.circle:
          canvas.drawCircle(const Offset(0, 0), p.size / 2, paint);
        case _ParticleShape.diamond:
          final path = Path()
            ..moveTo(0, -p.size / 2)
            ..lineTo(p.size / 2, 0)
            ..lineTo(0, p.size / 2)
            ..lineTo(-p.size / 2, 0)
            ..close();
          canvas.drawPath(path, paint);
        case _ParticleShape.square:
          canvas.drawRect(
            Rect.fromCenter(
              center: Offset.zero,
              width: p.size * 0.7,
              height: p.size * 0.7,
            ),
            paint,
          );
      }
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(covariant _ParticlePainter old) => old.time != time;
}
