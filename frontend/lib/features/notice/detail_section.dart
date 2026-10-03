import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class DetailSection extends StatelessWidget {
  const DetailSection({super.key, required this.title, required this.lines});
  final String title;
  final List<String> lines;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 24),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 10),
        ...lines.map(
          (line) => Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: SelectableText(
              line,
              style: const TextStyle(height: 1.6, color: AppColors.grey700),
            ),
          ),
        ),
      ],
    ),
  );
}
