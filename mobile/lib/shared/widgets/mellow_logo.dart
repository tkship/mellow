import 'package:flutter/material.dart';

/// Mellow 小猫 Logo — CustomPaint 简洁灵动风格
class MellowLogo extends StatelessWidget {
  final double size;
  final Color? color;

  const MellowLogo({super.key, this.size = 64, this.color});

  @override
  Widget build(BuildContext context) {
    final paintColor = color ?? Theme.of(context).colorScheme.primary;
    return CustomPaint(
      size: Size(size, size),
      painter: _MellowLogoPainter(paintColor),
    );
  }
}

class _MellowLogoPainter extends CustomPainter {
  final Color color;

  _MellowLogoPainter(this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final w = size.width;
    final h = size.height;

    // 猫头 — 圆润椭圆
    canvas.drawOval(
      Rect.fromLTWH(w * 0.18, h * 0.2, w * 0.64, h * 0.55),
      paint,
    );

    // 左耳 — 三角形
    final leftEar = Path()
      ..moveTo(w * 0.22, h * 0.28)
      ..lineTo(w * 0.12, h * 0.05)
      ..lineTo(w * 0.36, h * 0.22)
      ..close();
    canvas.drawPath(leftEar, paint);

    // 右耳 — 三角形
    final rightEar = Path()
      ..moveTo(w * 0.78, h * 0.28)
      ..lineTo(w * 0.88, h * 0.05)
      ..lineTo(w * 0.64, h * 0.22)
      ..close();
    canvas.drawPath(rightEar, paint);

    // 眼睛 — 白色圆点
    final eyePaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(w * 0.38, h * 0.42), w * 0.06, eyePaint);
    canvas.drawCircle(Offset(w * 0.62, h * 0.42), w * 0.06, eyePaint);

    // 瞳孔 — 深色小圆
    final pupilPaint = Paint()
      ..color = const Color(0xFF1A1A2E)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(w * 0.38, h * 0.43), w * 0.025, pupilPaint);
    canvas.drawCircle(Offset(w * 0.62, h * 0.43), w * 0.025, pupilPaint);

    // 鼻子 — 小三角
    final nosePaint = Paint()
      ..color = const Color(0xFFF09433)
      ..style = PaintingStyle.fill;
    final nose = Path()
      ..moveTo(w * 0.5, h * 0.52)
      ..lineTo(w * 0.47, h * 0.57)
      ..lineTo(w * 0.53, h * 0.57)
      ..close();
    canvas.drawPath(nose, nosePaint);

    // 嘴巴 — 弧线
    final mouthPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = w * 0.03;
    final mouth = Path()
      ..moveTo(w * 0.43, h * 0.62)
      ..quadraticBezierTo(w * 0.5, h * 0.7, w * 0.57, h * 0.62);
    canvas.drawPath(mouth, mouthPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
