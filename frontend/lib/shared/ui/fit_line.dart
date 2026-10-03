import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/notice.dart';

import 'app_colors.dart';

/// 제목 위 한 줄: AI 가 본 될 가능성과 추천 근거. 값이 없으면 아무것도 그리지 않는다.
class FitLine extends StatelessWidget {
  const FitLine({super.key, required this.notice, this.fontSize = 12});
  final Notice notice;
  final double fontSize;

  static Color colorFor(int chance) {
    if (chance >= 70) return AppColors.primary;
    if (chance >= 40) return AppColors.grey700;
    return AppColors.grey500;
  }

  @override
  Widget build(BuildContext context) {
    final chance = notice.chance;
    if (chance == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Text.rich(
        TextSpan(
          children: [
            TextSpan(
              text: '합격 가능성 $chance%',
              style: TextStyle(
                fontSize: fontSize,
                fontWeight: FontWeight.w700,
                color: colorFor(chance),
              ),
            ),
            if (notice.fitReason.isNotEmpty)
              TextSpan(
                text: '  ${notice.fitReason}',
                style: TextStyle(fontSize: fontSize, color: AppColors.grey500),
              ),
          ],
        ),
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
      ),
    );
  }
}
