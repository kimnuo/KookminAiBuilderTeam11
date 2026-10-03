import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_search.dart';

import 'category_tile.dart';

class CategoryGrid extends StatelessWidget {
  const CategoryGrid({
    super.key,
    required this.notices,
    required this.selected,
    required this.onSelect,
    required this.onOpen,
    required this.onNotice,
  });
  final List<Notice> notices;
  final Set<String> selected;
  final ValueChanged<String> onSelect;
  final ValueChanged<NoticeGroup> onOpen;
  final ValueChanged<Notice> onNotice;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, size) {
      final columns = size.maxWidth >= 900 ? 3 : 2;
      final rows = (noticeGroups.length / columns).ceil();
      final gap = size.maxHeight < 350 ? 8.0 : 14.0;
      final height = (size.maxHeight - gap * (rows - 1)) / rows;
      return GridView.count(
        crossAxisCount: columns,
        physics: const NeverScrollableScrollPhysics(),
        padding: EdgeInsets.zero,
        mainAxisSpacing: gap,
        crossAxisSpacing: gap,
        childAspectRatio:
            ((size.maxWidth - gap * (columns - 1)) / columns) / height,
        children: noticeGroups
            .map(
              (group) => CategoryTile(
                group: group,
                notices: notices
                    .where((n) => groupsFor(n).any((g) => g.id == group.id))
                    .toList(),
                selected: selected.contains(group.id),
                onSelect: () => onSelect(group.id),
                onOpen: () => onOpen(group),
                onNotice: onNotice,
              ),
            )
            .toList(),
      );
    },
  );
}
