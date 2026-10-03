import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';

import 'notice_row.dart';

class CategoryDialog extends StatefulWidget {
  const CategoryDialog({
    super.key,
    required this.title,
    required this.notices,
    required this.onNotice,
  });
  final String title;
  final List<Notice> notices;
  final ValueChanged<Notice> onNotice;
  @override
  State<CategoryDialog> createState() => _CategoryDialogState();
}

class _CategoryDialogState extends State<CategoryDialog> {
  int _page = 0;
  @override
  Widget build(BuildContext context) => Dialog(
    insetPadding: const EdgeInsets.all(16),
    child: SizedBox(
      width: 920,
      height: MediaQuery.sizeOf(context).height * .85,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            _header(),
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                '${widget.notices.length}개의 공고 · 공고를 누르면 자세히 볼 수 있어요',
              ),
            ),
            const SizedBox(height: 20),
            Expanded(child: _list()),
            _pagination(),
          ],
        ),
      ),
    ),
  );

  Widget _header() => Row(
    children: [
      Expanded(
        child: Text(
          widget.title,
          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
        ),
      ),
      IconButton(
        tooltip: '닫기',
        onPressed: () => Navigator.pop(context),
        icon: const Icon(Icons.close_rounded),
      ),
    ],
  );

  Widget _list() {
    if (widget.notices.isEmpty) {
      return const Center(child: Text('조건에 맞는 공고가 없어요.'));
    }
    final items = widget.notices
        .skip(_page * FeedConfig.pageSize)
        .take(FeedConfig.pageSize)
        .toList();
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, i) => NoticeRow(
        notice: items[i],
        onOpen: () {
          Navigator.pop(context);
          widget.onNotice(items[i]);
        },
      ),
    );
  }

  Widget _pagination() {
    final pages = math.max(
      1,
      (widget.notices.length / FeedConfig.pageSize).ceil(),
    );
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          tooltip: '이전 페이지',
          onPressed: _page == 0 ? null : () => setState(() => _page--),
          icon: const Icon(Icons.chevron_left_rounded),
        ),
        Text('${_page + 1} / $pages'),
        IconButton(
          tooltip: '다음 페이지',
          onPressed: _page + 1 >= pages ? null : () => setState(() => _page++),
          icon: const Icon(Icons.chevron_right_rounded),
        ),
      ],
    );
  }
}
