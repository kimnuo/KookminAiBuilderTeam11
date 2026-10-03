import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/notice_api.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/open_original.dart';

import 'notice_content.dart';
import 'package:kmu_notice/shared/lib/feed_path.dart';

class NoticePage extends StatefulWidget {
  const NoticePage({
    super.key,
    required this.id,
    required this.preparation,
    this.onClose,
  });
  final String id;
  final VoidCallback? onClose;
  final Widget Function(Notice) preparation;
  @override
  State<NoticePage> createState() => _NoticePageState();
}

class _NoticePageState extends State<NoticePage> {
  late Future<Notice> _notice;
  @override
  void initState() {
    super.initState();
    _notice = NoticeApi.detail(widget.id);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: const Color(0xFFF5F7FA),
    appBar: _header(),
    body: FutureBuilder(
      future: _notice,
      builder: (_, snapshot) {
        if (snapshot.hasError) return _error();
        final notice = snapshot.data;
        if (notice == null) {
          return const Center(child: CircularProgressIndicator());
        }
        return _content(notice);
      },
    ),
  );

  AppBar _header() => AppBar(
    title: const Text(
      '크노 · 공고 상세',
      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
    ),
    automaticallyImplyLeading: false,
    leading: widget.onClose != null
        ? null
        : IconButton(
            tooltip: '대시보드로 돌아가기',
            icon: const Icon(Icons.arrow_back_rounded),
            onPressed: () => context.canPop()
                ? context.pop()
                : context.go(feedPath),
          ),
    actions: [
      if (widget.onClose != null)
        Padding(
          padding: const EdgeInsets.only(right: 8),
          child: IconButton(
            tooltip: '닫기',
            onPressed: widget.onClose,
            icon: const Icon(Icons.close_rounded),
          ),
        ),
    ],
  );

  Widget _content(Notice notice) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1050),
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(28),
                child: NoticeContent(
                  notice: notice,
                  preparation: widget.preparation(notice),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: () => _original(notice),
                  icon: const Icon(Icons.open_in_new_rounded),
                  label: const Text('원문에서 확인하기'),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _error() => Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Text('공고를 불러오지 못했어요.'),
        TextButton(
          onPressed: () =>
              setState(() => _notice = NoticeApi.detail(widget.id)),
          child: const Text('다시 시도'),
        ),
      ],
    ),
  );
  Future<void> _original(Notice notice) async {
    final opened = await openOriginal(notice.url);
    if (!opened && mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('원문 링크를 열 수 없어요.')));
    }
  }
}
