import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:kmu_notice/features/feed/feed_page.dart';
import 'package:kmu_notice/shared/api/notice_api.dart';

import 'support/notice_fixture.dart';

void main() {
  _layoutTests();
  _homeTest();
}

void _layoutTests() {
  for (final size in [
    const Size(1280, 720),
    const Size(390, 844),
    const Size(320, 568),
  ]) {
    testWidgets('6개 카드가 ${size.width}×${size.height} 한 화면에 표시', (tester) async {
      await _pump(tester, size);
      for (final label in ['학사·생활', '졸업', '장학', '취업', '행사·대외활동', '기타']) {
        final rect = tester.getRect(find.text(label));
        expect(rect.top, greaterThanOrEqualTo(0));
        expect(rect.bottom, lessThanOrEqualTo(size.height));
      }
      final academic = tester.getTopLeft(find.text('학사·생활'));
      final graduation = tester.getTopLeft(find.text('졸업'));
      final scholarship = tester.getTopLeft(find.text('장학'));
      expect(academic.dy, graduation.dy);
      expect(
        scholarship.dy,
        size.width >= 900 ? academic.dy : greaterThan(academic.dy),
      );
      expect(tester.takeException(), isNull);
    });
  }
}

void _homeTest() {
  testWidgets('크노 로고는 검색 입력과 선택을 초기화한다', (tester) async {
    await _pump(tester, const Size(1280, 720));
    await tester.enterText(find.byType(TextField), '없는단어');
    await tester.tap(find.byType(Checkbox).first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('크노'));
    await tester.pumpAndSettle();
    expect(
      tester.widget<TextField>(find.byType(TextField)).controller?.text ?? '',
      '',
    );
    expect(find.text('모든 카테고리'), findsOneWidget);
    expect(find.text('전체 공고 1'), findsOneWidget);
  });
}

Future<void> _pump(WidgetTester tester, Size size) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  NoticeApi.client = MockClient(
    (_) async => http.Response.bytes(
      utf8.encode(
        jsonEncode({
          'items': [serverNotice()],
        }),
      ),
      200,
    ),
  );
  addTearDown(() {
    NoticeApi.client.close();
    NoticeApi.client = http.Client();
  });
  await tester.pumpWidget(MaterialApp(home: FeedPage(onNotice: (_) {})));
  await tester.pumpAndSettle();
}
