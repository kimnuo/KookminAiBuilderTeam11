import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kmu_notice/features/feed/category_dialog.dart';
import 'package:kmu_notice/features/feed/category_tile.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';

import 'support/notice_fixture.dart';

void main() {
  _previewTest();
  _titleTest();
  _scrollTest();
  _mobileTest();
  _emptyTest();
}

void _previewTest() {
  testWidgets('첫 화면에는 3개 미리보기와 전체 개수를 표시한다', (tester) async {
    await _pump(tester);
    for (var i = 1; i <= 3; i++) {
      expect(find.text('검증 공고 $i'), findsOneWidget);
    }
    expect(find.text('검증 공고 4'), findsNothing);
    expect(find.text('12개'), findsOneWidget);
    expect(find.text('전체 공고 보기 ›'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

void _titleTest() {
  testWidgets('카테고리 이름을 누르면 3개를 넘는 전체 목록이 열린다', (tester) async {
    await _pump(tester);
    await tester.tap(find.text('학사·생활'));
    await tester.pumpAndSettle();
    expect(find.byType(CategoryDialog), findsOneWidget);
    expect(find.text('12개의 공고 · 공고를 누르면 자세히 볼 수 있어요'), findsOneWidget);
    expect(find.text('검증 공고 4'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

void _scrollTest() {
  testWidgets('전체 보기에서 8개를 넘어 마지막 공고까지 스크롤하고 연다', (tester) async {
    Notice? opened;
    await _pump(tester, onNotice: (notice) => opened = notice);
    await tester.tap(find.text('전체 공고 보기 ›'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('검증 공고 12'),
      250,
      scrollable: find.byType(Scrollable),
    );
    await tester.tap(find.text('검증 공고 12'));
    await tester.pumpAndSettle();
    expect(opened?.id, 'category-12');
    expect(find.byType(CategoryDialog), findsNothing);
    expect(tester.takeException(), isNull);
  });
}

void _mobileTest() {
  testWidgets('320×568 작은 화면에서도 전체 보기와 목록 스크롤이 동작한다', (tester) async {
    await _pump(tester, size: const Size(320, 568), tiny: true);
    await tester.tap(find.text('전체 보기 ›'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('검증 공고 12'),
      250,
      scrollable: find.byType(Scrollable),
    );
    expect(find.text('검증 공고 12'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

void _emptyTest() {
  testWidgets('빈 카테고리는 전체 보기에서 빈 목록을 안내한다', (tester) async {
    await _pump(tester, count: 0);
    await tester.tap(find.text('전체 공고 보기 ›'));
    await tester.pumpAndSettle();
    expect(find.text('조건에 맞는 공고가 없어요.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

Future<void> _pump(
  WidgetTester tester, {
  Size size = const Size(1280, 720),
  bool tiny = false,
  int count = 12,
  ValueChanged<Notice>? onNotice,
}) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  final notices = List.generate(
    count,
    (i) => Notice(
      serverNotice(
        id: 'category-${i + 1}',
        digest: {'title': '검증 공고 ${i + 1}'},
      ),
    ),
  );
  await tester.pumpWidget(
    MaterialApp(
      home: Builder(
        builder: (context) => _card(context, notices, tiny, onNotice ?? (_) {}),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

Widget _card(
  BuildContext context,
  List<Notice> notices,
  bool tiny,
  ValueChanged<Notice> onNotice,
) => Scaffold(
  body: Center(
    child: SizedBox(
      width: tiny ? 140 : 360,
      height: tiny ? 80 : 260,
      child: CategoryTile(
        group: noticeGroups.first,
        notices: notices,
        selected: false,
        onSelect: () {},
        onNotice: onNotice,
        onOpen: () => showDialog<void>(
          context: context,
          builder: (_) => CategoryDialog(
            title: '학사·생활',
            notices: notices,
            onNotice: onNotice,
          ),
        ),
      ),
    ),
  ),
);
