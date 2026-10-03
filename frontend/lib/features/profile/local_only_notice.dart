import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class LocalOnlyNotice extends StatelessWidget {
  const LocalOnlyNotice({
    super.key,
    this.text = '이력은 이 기기에만 저장돼요. 서버에는 고른 태그만 올라가요.',
  });

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.primaryLight,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.lock_rounded, size: 20, color: AppColors.primary),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 14,
                height: 1.5,
                color: AppColors.grey700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
