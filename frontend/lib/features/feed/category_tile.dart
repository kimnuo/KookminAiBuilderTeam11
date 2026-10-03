import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

class CategoryTile extends StatelessWidget {
  const CategoryTile({
    super.key,
    required this.group,
    required this.notices,
    required this.selected,
    required this.onSelect,
    required this.onOpen,
  });
  final NoticeGroup group;
  final List<Notice> notices;
  final bool selected;
  final VoidCallback onSelect, onOpen;
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
            child: _content(size.maxHeight, tiny),
          ),
        ),
      );
    },
  );
  Widget _content(double height, bool tiny) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      _top(tiny),
      if (!tiny) ...[const SizedBox(height: 8), _label(15)],
      const Spacer(),
      if (height > 155 && notices.isNotEmpty) ...[
        Text(
          notices.first.title,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontSize: 13, color: AppColors.grey700),
        ),
        const SizedBox(height: 8),
      ],
      _bottom(height, tiny),
    ],
  );
  Widget _top(bool tiny) => Row(
    children: [
      if (!tiny) ...[
        Icon(group.icon, color: group.color, size: 24),
        const Spacer(),
      ],
      if (tiny) Expanded(child: _label(12)),
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
  Widget _bottom(double height, bool tiny) => Row(
    children: [
      Text(
        '${notices.length}개',
        style: TextStyle(
          fontSize: tiny ? 12 : 17,
          fontWeight: FontWeight.w700,
          color: group.color,
        ),
      ),
      const Spacer(),
      if (height > 185 && notices.isNotEmpty)
        Text(
          deadlineLabel(notices.first),
          style: const TextStyle(fontSize: 11, color: AppColors.grey500),
        ),
      Icon(
        Icons.chevron_right_rounded,
        size: tiny ? 14 : 20,
        color: AppColors.grey500,
      ),
    ],
  );
  Widget _label(double size) => Text(
    group.label,
    maxLines: 1,
    overflow: TextOverflow.ellipsis,
    style: TextStyle(fontSize: size, fontWeight: FontWeight.w700),
  );
}
