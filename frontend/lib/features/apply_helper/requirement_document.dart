import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class RequirementDocument extends StatelessWidget {
  const RequirementDocument({super.key, required this.document});
  final Map<String, dynamic> document;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 18),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          document['name'] as String,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        if (document['condition'] is String)
          Text('조건: ${document['condition']}'),
        const SizedBox(height: 6),
        Text(
          '근거: ${document['evidence']}',
          style: const TextStyle(
            fontSize: 12,
            color: AppColors.grey700,
            height: 1.5,
          ),
        ),
      ],
    ),
  );
}
