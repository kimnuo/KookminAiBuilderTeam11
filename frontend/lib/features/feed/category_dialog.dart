import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/notice.dart';

import 'notice_row.dart';

class CategoryDialog extends StatelessWidget {
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
  Widget build(BuildContext context) => Dialog(
    insetPadding: const EdgeInsets.all(16),
    child: SizedBox(
      width: 920,
      height: MediaQuery.sizeOf(context).height * .85,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            _header(context),
            Align(
              alignment: Alignment.centerLeft,
              child: Text('${notices.length}개의 공고 · 공고를 누르면 자세히 볼 수 있어요'),
            ),
            const SizedBox(height: 20),
            Expanded(child: _list()),
          ],
        ),
      ),
    ),
  );

  Widget _header(BuildContext context) => Row(
    children: [
      Expanded(
        child: Text(
          title,
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
    if (notices.isEmpty) {
      return const Center(child: Text('조건에 맞는 공고가 없어요.'));
    }
    return ListView.builder(
      itemCount: notices.length,
      itemBuilder: (context, i) => NoticeRow(
        notice: notices[i],
        onOpen: () {
          Navigator.pop(context);
          onNotice(notices[i]);
        },
      ),
    );
  }
}
