import 'package:flutter/material.dart';

import 'app_colors.dart';

/// Shared styles extracted from the original main.dart
final text1 = TextStyle(
  color: AppColors.colorText1,
  fontFamily: 'Lato',
  fontSize: 12,
  fontWeight: FontWeight.w200,
);
final text2 = TextStyle(
  color: AppColors.colorText2,
  fontFamily: 'Lato',
  fontSize: 12,
  fontWeight: FontWeight.w200,
);

double get appScale => _appScale;
double _appScale = 1;
