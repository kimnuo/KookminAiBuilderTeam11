import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';

import 'feed_controller.dart';
import 'feed_select_button.dart';

class FeedToolbar extends StatelessWidget {
  const FeedToolbar({
    super.key,
    required this.controller,
    required this.onOpen,
  });
  final FeedController controller;
  final VoidCallback onOpen;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (_, size) {
      if (size.maxWidth < 680) {
        return Column(
          children: [
            SizedBox(height: 44, child: _search()),
            const SizedBox(height: 8),
            SizedBox(height: 40, child: _controls(true)),
          ],
        );
      }
      return SizedBox(
        height: 48,
        child: Row(
          children: [
            Expanded(child: _search()),
            const SizedBox(width: 12),
            _controls(false),
          ],
        ),
      );
    },
  );
  Widget _search() => TextField(
    onChanged: controller.setQuery,
    decoration: InputDecoration(
      hintText: '제목, 키워드, 카테고리 검색',
      prefixIcon: const Icon(Icons.search_rounded),
      filled: true,
      fillColor: Colors.white,
      isDense: true,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
    ),
  );
  Widget _controls(bool compact) => Row(
    children: [
      if (!compact) ...[
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 185),
          child: FeedSelectButton(
            value: controller.source,
            options: {'': '모든 출처', ...controller.sources},
            tooltip: '출처 선택',
            icon:
                (controller.sources[controller.source]?.contains('사업단') ??
                    false)
                ? Icons.school_rounded
                : Icons.filter_alt_outlined,
            onChanged: controller.setSource,
          ),
        ),
        const SizedBox(width: 8),
      ],
      FeedSelectButton(
        value: controller.sort,
        options: FeedConfig.sortOptions,
        tooltip: '정렬 선택',
        icon: Icons.swap_vert_rounded,
        onChanged: controller.setSort,
        compact: compact,
      ),
      if (compact) const Spacer() else const SizedBox(width: 12),
      FilledButton(
        onPressed: onOpen,
        child: Text(
          '${controller.selected.isEmpty ? '전체' : '선택'} 공고 ${controller.chosen.length}',
        ),
      ),
    ],
  );
}
