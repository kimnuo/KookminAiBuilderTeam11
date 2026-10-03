import 'package:flutter/material.dart';

import 'feed_controller.dart';

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
      if (!compact) _sources(),
      SizedBox(
        width: compact ? 115 : 135,
        child: DropdownButton<String>(
          value: controller.sort,
          isExpanded: true,
          underline: const SizedBox(),
          items: const [
            DropdownMenuItem(value: 'recommend', child: Text('추천 순')),
            DropdownMenuItem(value: 'deadline', child: Text('마감 임박 순')),
          ],
          onChanged: (v) => controller.setSort(v ?? 'recommend'),
        ),
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
  Widget _sources() => SizedBox(
    width: 160,
    child: DropdownButton<String>(
      value: controller.source,
      isExpanded: true,
      underline: const SizedBox(),
      items: [
        const DropdownMenuItem(value: '', child: Text('모든 출처')),
        ...controller.sources.entries.map(
          (e) => DropdownMenuItem(
            value: e.key,
            child: Text(e.value, overflow: TextOverflow.ellipsis),
          ),
        ),
      ],
      onChanged: (v) => controller.setSource(v ?? ''),
    ),
  );
}
