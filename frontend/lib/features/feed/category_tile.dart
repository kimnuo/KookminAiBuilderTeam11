import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

import 'category_previews.dart';

class CategoryTile extends StatelessWidget {
  const CategoryTile({
    super.key,
    required this.group,
    required this.notices,
    required this.selected,
    required this.onSelect,
    required this.onOpen,
    required this.onNotice,
  });
  final NoticeGroup group;
  final List<Notice> notices;
  final bool selected;
  final VoidCallback onSelect, onOpen;
  final ValueChanged<Notice> onNotice;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (_, size) {
      final tiny = size.maxHeight < 100;
      return Material(
        color: selected ? AppColors.primaryLight : Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: BorderSide(
            color: selected ? AppColors.primary : const Color(0xFFE8ECF0),
          ),
        ),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onOpen,
          child: Padding(
            padding: EdgeInsets.all(tiny ? (size.maxHeight < 65 ? 4 : 8) : 14),
            child: _content(tiny),
          ),
        ),
      );
    },
  );
  Widget _content(bool tiny) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      _top(tiny),
      if (!tiny) ...[
        const SizedBox(height: 10),
        Expanded(
          child: CategoryPreviews(notices: notices, onNotice: onNotice),
        ),
        const SizedBox(height: 6),
      ] else
        const Spacer(),
      _bottom(tiny),
    ],
  );
  Widget _top(bool tiny) => Row(
    children: [
      if (!tiny) ...[
        Icon(group.icon, color: group.color, size: 22),
        const SizedBox(width: 8),
      ],
      Expanded(
        child: Text(
          group.label,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontSize: tiny ? 12 : 14,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      SizedBox(
        width: 28,
        height: 28,
        child: Checkbox(
          semanticLabel: '${group.label} 함께 선택',
          value: selected,
          onChanged: (_) => onSelect(),
          visualDensity: VisualDensity.compact,
        ),
      ),
    ],
  );
  Widget _bottom(bool tiny) => Row(
    children: [
      Text(
        '${notices.length}개',
        style: TextStyle(
          fontSize: tiny ? 12 : 15,
          fontWeight: FontWeight.w700,
          color: group.color,
        ),
      ),
      const Spacer(),
      if (!tiny)
        const Text(
          '더 보기',
          style: TextStyle(fontSize: 11, color: AppColors.grey500),
        ),
      Icon(
        Icons.chevron_right_rounded,
        size: tiny ? 14 : 18,
        color: AppColors.grey500,
      ),
    ],
  );
}
