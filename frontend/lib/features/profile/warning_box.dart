import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class WarningBox extends StatelessWidget {
  const WarningBox(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF4E5),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.error_rounded, size: 20, color: Color(0xFFFF9500)),
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
