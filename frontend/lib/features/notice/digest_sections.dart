import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/digest_items.dart';
import 'package:kmu_notice/shared/lib/notice.dart';

import 'detail_section.dart';

class DigestSections extends StatelessWidget {
  const DigestSections({super.key, required this.notice});
  final Notice notice;
  @override
  Widget build(BuildContext context) {
    final points = notice.keyPoints
        .where((p) => !isApplicationPoint(p))
        .toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (points.isNotEmpty)
          DetailSection(title: '주요 내역', lines: points.map(_point).toList()),
        if (notice.requiredActions.isNotEmpty)
          DetailSection(
            title: '필수 사항',
            lines: notice.requiredActions.map(_action).toList(),
          ),
      ],
    );
  }

  String _point(Map<String, dynamic> item) =>
      '${item['label']}: ${item['value']}\n근거: ${item['evidence']}';
  String _action(Map<String, dynamic> item) {
    final origin = item['origin'];
    final source = origin is String && origin.trim().isNotEmpty
        ? ' ($origin)'
        : '';
    return '${item['text']}$source\n근거: ${item['evidence']}';
  }
}
