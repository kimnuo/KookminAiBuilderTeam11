import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

class NoticeRow extends StatelessWidget {
  const NoticeRow({super.key, required this.notice, required this.onOpen});
  final Notice notice;
  final VoidCallback onOpen;
  @override
  Widget build(BuildContext context) => Card(
    elevation: 0,
    color: AppColors.surface,
    margin: const EdgeInsets.only(bottom: 10),
    child: ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
      onTap: onOpen,
      title: Text(
        notice.title,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 8),
        child: Text(
          '${notice.sourceName} · ${deadlineLabel(notice)}'
          '${notice.reasons.isEmpty ? '' : '\n${notice.reasons.first}'}',
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        ),
      ),
      trailing: const Icon(Icons.chevron_right_rounded),
    ),
  );
}
