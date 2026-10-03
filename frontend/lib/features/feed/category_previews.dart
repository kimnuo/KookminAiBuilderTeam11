import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

class CategoryPreviews extends StatelessWidget {
  const CategoryPreviews({
    super.key,
    required this.notices,
    required this.onNotice,
  });
  final List<Notice> notices;
  final ValueChanged<Notice> onNotice;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (_, size) {
      if (notices.isEmpty) {
        return const Align(
          alignment: Alignment.topLeft,
          child: Text(
            '아직 등록된 공고가 없어요',
            style: TextStyle(fontSize: 12, color: AppColors.grey500),
          ),
        );
      }
      final rowHeight = size.maxHeight >= FeedConfig.previewRowHeight * 2
          ? FeedConfig.previewRowHeight
          : FeedConfig.compactPreviewRowHeight;
      final count = math.min(
        notices.length,
        math.min(FeedConfig.previewCount, (size.maxHeight / rowHeight).floor()),
      );
      if (count < 1) return const SizedBox.shrink();
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: notices.take(count).map((n) => _row(n, rowHeight)).toList(),
      );
    },
  );

  Widget _row(Notice notice, double rowHeight) => SizedBox(
    height: rowHeight,
    child: InkWell(
      borderRadius: BorderRadius.circular(8),
      onTap: () => onNotice(notice),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 2),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Padding(
              padding: EdgeInsets.only(top: 6, right: 6),
              child: Icon(Icons.circle, size: 4, color: AppColors.grey500),
            ),
            Expanded(
              child: Text(
                notice.title,
                maxLines: rowHeight < FeedConfig.previewRowHeight ? 1 : 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 12,
                  height: 1.4,
                  color: AppColors.grey700,
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}
