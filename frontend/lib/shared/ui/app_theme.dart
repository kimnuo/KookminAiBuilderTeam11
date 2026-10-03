import 'package:flutter/material.dart';

import 'app_colors.dart';

ThemeData buildAppTheme() {
  final base = ThemeData(
    useMaterial3: true,
    fontFamily: 'Pretendard',
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      primary: AppColors.primary,
      surface: AppColors.background,
    ),
    scaffoldBackgroundColor: AppColors.background,
  );
  return base.copyWith(
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.background,
      foregroundColor: AppColors.grey900,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
    ),
    textTheme: base.textTheme.apply(
      bodyColor: AppColors.grey900,
      displayColor: AppColors.grey900,
    ),
  );
}
