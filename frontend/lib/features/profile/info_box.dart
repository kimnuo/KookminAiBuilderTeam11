import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class InfoBox extends StatelessWidget {
  const InfoBox({super.key, required this.rows});

  final List<(String, String)> rows;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 4),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final (label, body) in rows) ...[
            Text(
              label,
              style: const TextStyle(fontSize: 13, color: AppColors.grey500),
            ),
            const SizedBox(height: 4),
            Text(body, style: const TextStyle(fontSize: 15, height: 1.5)),
            const SizedBox(height: 16),
          ],
        ],
      ),
    );
  }
}
