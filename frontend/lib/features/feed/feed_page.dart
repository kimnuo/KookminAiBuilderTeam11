import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_search.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

import 'feed_controller.dart';
import 'dashboard_header.dart';
import 'feed_toolbar.dart';
import 'category_grid.dart';
import 'category_dialog.dart';

class FeedPage extends StatefulWidget {
  const FeedPage({super.key, required this.onNotice});
  final ValueChanged<Notice> onNotice;
  @override
  State<FeedPage> createState() => _FeedPageState();
}

class _FeedPageState extends State<FeedPage> {
  final _controller = FeedController();
  @override
  void initState() {
    super.initState();
    _controller.load();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: const Color(0xFFF5F7FA),
    body: SafeArea(
      child: LayoutBuilder(
        builder: (context, size) => Padding(
          padding: EdgeInsets.all(size.maxWidth < 680 ? 12 : 28),
          child: ListenableBuilder(
            listenable: _controller,
            builder: (_, _) => _dashboard(size),
          ),
        ),
      ),
    ),
  );

  Widget _dashboard(BoxConstraints size) {
    final compact = size.maxWidth < 680 || size.maxHeight < 600;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DashboardHeader(compact: compact),
        if (FeedConfig.demo)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              '더미 데이터 미리보기 · 실제 공고가 아니에요',
              style: TextStyle(
                fontSize: compact ? 11 : 12,
                color: AppColors.grey500,
              ),
            ),
          ),
        SizedBox(height: compact ? 8 : 20),
        FeedToolbar(
          controller: _controller,
          onOpen: () => _open('선택한 공고', _controller.chosen),
        ),
        SizedBox(height: compact ? 6 : 14),
        _selection(compact),
        const SizedBox(height: 8),
        Expanded(child: _content()),
        const SizedBox(height: 8),
        Text(
          '카드를 누르면 더 보기 · 체크박스로 여러 카테고리를 함께 선택하세요',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontSize: compact ? 10 : 12,
            color: AppColors.grey500,
          ),
        ),
      ],
    );
  }

  Widget _selection(bool compact) => SizedBox(
    height: compact ? 28 : 32,
    child: Row(
      children: [
        Expanded(
          child: Text(
            _controller.selected.isEmpty
                ? '모든 카테고리'
                : '${_controller.selected.length}개 카테고리 선택 · 공고 ${_controller.chosen.length}개',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ),
        if (_controller.selected.isNotEmpty)
          TextButton(
            onPressed: _controller.clearSelection,
            child: const Text('선택 해제'),
          ),
        if (!compact || _controller.selected.isEmpty)
          Text(
            '${_controller.visible.length}개의 소식',
            style: const TextStyle(color: AppColors.grey500),
          ),
      ],
    ),
  );

  Widget _content() {
    if (_controller.loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_controller.error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_controller.error!),
            TextButton(onPressed: _controller.load, child: const Text('다시 시도')),
          ],
        ),
      );
    }
    return CategoryGrid(
      notices: _controller.visible,
      selected: _controller.selected,
      onSelect: _controller.toggle,
      onOpen: (g) => _open(
        g.label,
        _controller.visible
            .where((n) => groupsFor(n).any((group) => group.id == g.id))
            .toList(),
      ),
    );
  }

  void _open(String title, List<Notice> notices) => showDialog<void>(
    context: context,
    builder: (_) => CategoryDialog(
      title: title,
      notices: notices,
      onNotice: widget.onNotice,
    ),
  );
}
