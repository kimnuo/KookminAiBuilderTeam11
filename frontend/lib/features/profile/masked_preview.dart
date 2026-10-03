import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'pii_masker.dart';

class MaskedPreview extends StatelessWidget {
  const MaskedPreview({super.key, required this.result});

  final MaskResult result;

  @override
  Widget build(BuildContext context) {
    final summary = result.counts.entries
        .where((e) => e.value > 0)
        .map((e) => '${e.key} ${e.value}곳')
        .join(', ');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          summary.isEmpty ? '가릴 정보를 찾지 못했어요' : '$summary을 가렸어요',
          style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        Container(
          constraints: const BoxConstraints(maxHeight: 280),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(16),
          ),
          child: SingleChildScrollView(
            child: Text(
              result.text,
              style: const TextStyle(
                fontSize: 13,
                height: 1.6,
                color: AppColors.grey700,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          '이 글만 AI로 보내요. 원본 PDF는 보내지 않아요.',
          style: TextStyle(fontSize: 13, color: AppColors.grey500),
        ),
      ],
    );
  }
}
