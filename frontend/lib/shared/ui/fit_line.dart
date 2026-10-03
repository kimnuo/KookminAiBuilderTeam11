import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/notice.dart';

import 'app_colors.dart';

/// 될 가능성에 따른 색. 70 이상 파랑, 40 이상 진회색, 그 아래는 흐리게.
Color chanceColor(int chance) {
  if (chance >= 70) return AppColors.primary;
  if (chance >= 40) return AppColors.grey700;
  return AppColors.grey500;
}

Color chanceBackground(int chance) {
  if (chance >= 70) return AppColors.primaryLight;
  return AppColors.surface;
}

/// 목록에서 제목 위에 붙는 작은 알약: 「합격 가능성 72%」 + 근거 한 줄.
class FitLine extends StatelessWidget {
  const FitLine({super.key, required this.notice});
  final Notice notice;

  @override
  Widget build(BuildContext context) {
    final chance = notice.chance;
    if (chance == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: chanceBackground(chance),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              '합격 가능성 $chance%',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: chanceColor(chance),
              ),
            ),
          ),
          if (notice.fitReason.isNotEmpty) ...[
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                notice.fitReason,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 12.5, color: AppColors.grey500),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

/// 상세 화면 맨 위 칸: 퍼센트를 크게 쓰고 근거와 추천 이유를 함께 보여 준다.
class FitCard extends StatelessWidget {
  const FitCard({super.key, required this.notice});
  final Notice notice;

  @override
  Widget build(BuildContext context) {
    final chance = notice.chance;
    if (chance == null) return const SizedBox.shrink();
    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: chanceBackground(chance),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                '$chance%',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.w800,
                  color: chanceColor(chance),
                  height: 1.1,
                ),
              ),
              const SizedBox(width: 8),
              const Text(
                '합격 가능성',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: AppColors.grey700,
                ),
              ),
            ],
          ),
          if (notice.fitReason.isNotEmpty) ...[
            const SizedBox(height: 10),
            SelectableText(
              notice.fitReason,
              style: const TextStyle(
                fontSize: 14.5,
                height: 1.6,
                color: AppColors.grey900,
              ),
            ),
          ],
          ...notice.reasons.map(
            (reason) => Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Text(
                '· $reason',
                style: const TextStyle(fontSize: 13.5, color: AppColors.grey700),
              ),
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'AI 가 내 학과·학년·관심 분야와 공고 조건을 맞춰 본 값이에요. 참고용이에요.',
            style: TextStyle(fontSize: 12, color: AppColors.grey500),
          ),
        ],
      ),
    );
  }
}
