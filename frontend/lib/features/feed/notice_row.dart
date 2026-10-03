import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/fit_line.dart';

class NoticeRow extends StatelessWidget {
  const NoticeRow({super.key, required this.notice, required this.onOpen});
  final Notice notice;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) => Card(
    elevation: 0,
    color: AppColors.surface,
    margin: const EdgeInsets.only(bottom: 12),
    child: InkWell(
      onTap: onOpen,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(18, 16, 14, 16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  FitLine(notice: notice),
                  Text(
                    notice.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      height: 1.45,
                      color: AppColors.grey900,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${notice.sourceName} · ${deadlineLabel(notice)}',
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppColors.grey500,
                    ),
                  ),
                  if (notice.reasons.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      notice.reasons.first,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 13,
                        color: AppColors.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(width: 10),
            const Icon(
              Icons.chevron_right_rounded,
              color: AppColors.grey500,
            ),
          ],
        ),
      ),
    ),
  );
}
