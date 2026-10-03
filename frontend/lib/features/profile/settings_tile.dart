import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class SettingsTile extends StatelessWidget {
  const SettingsTile({
    super.key,
    required this.label,
    required this.onTap,
    this.danger = false,
  });

  final String label;
  final VoidCallback onTap;
  final bool danger;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
        child: Row(
          children: [
            Expanded(
              child: Text(
                label,
                style: TextStyle(
                  fontSize: 17,
                  color: danger ? AppColors.danger : AppColors.grey900,
                ),
              ),
            ),
            if (!danger)
              const Icon(Icons.chevron_right_rounded, color: AppColors.grey300),
          ],
        ),
      ),
    );
  }
}
