import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'profile_analysis.dart';

const _kindLabels = {'projects': '프로젝트', 'awards': '수상', 'activities': '활동'};

class ReviewItemCard extends StatelessWidget {
  const ReviewItemCard({super.key, required this.item, required this.onTap});

  final AnalysisItem item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: item.keep ? AppColors.background : AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: item.keep ? AppColors.primary : AppColors.surface,
            width: 1.5,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.check_circle_rounded,
              color: item.keep ? AppColors.primary : AppColors.grey300,
            ),
            const SizedBox(width: 12),
            Expanded(child: _body()),
          ],
        ),
      ),
    );
  }

  Widget _body() {
    final sub = [_kindLabels[item.kind], item.detail].whereType<String>();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          item.title,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 2),
        Text(
          sub.join(' · '),
          style: const TextStyle(fontSize: 13, color: AppColors.grey500),
        ),
        const SizedBox(height: 8),
        Text(
          '근거: "${item.evidence}"',
          style: const TextStyle(
            fontSize: 13,
            height: 1.5,
            color: AppColors.grey700,
          ),
        ),
      ],
    );
  }
}
