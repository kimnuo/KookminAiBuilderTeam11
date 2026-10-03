import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class KnoHomeButton extends StatelessWidget {
  const KnoHomeButton({super.key, required this.onPressed});
  final VoidCallback onPressed;
  @override
  Widget build(BuildContext context) => Tooltip(
    message: '홈으로',
    child: TextButton(
      onPressed: onPressed,
      style: TextButton.styleFrom(
        foregroundColor: AppColors.grey900,
        padding: const EdgeInsets.symmetric(vertical: 6),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.blur_on_rounded, color: AppColors.primary, size: 30),
          SizedBox(width: 8),
          Text(
            '크노',
            style: TextStyle(fontSize: 25, fontWeight: FontWeight.w700),
          ),
        ],
      ),
    ),
  );
}
