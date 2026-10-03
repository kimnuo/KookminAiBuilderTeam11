import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:kmu_notice/features/apply_helper/apply_panel.dart';
import 'package:kmu_notice/features/apply_helper/requirements.dart';
import 'package:kmu_notice/features/feed/feed_controller.dart';
import 'package:kmu_notice/shared/api/notice_api.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'support/notice_fixture.dart';

final _actions = List.generate(
  4,
  (i) => {'text': '검증용 전공 변경 준비 ${i + 1}', 'evidence': '예시 원문 근거 ${i + 1}'},
);

void main() {
  _actionTests();
  _panelTest();
  _orderTest();
  _sourceTest();
}

void _actionTests() {
  test('서버의 text/evidence 준비 항목 4개를 읽는다', () {
    expect(
      requirementActions({'requirements': _actions}, Notice(serverNotice())),
      hasLength(4),
    );
  });
  test('공고 digest의 준비 항목은 근거를 검사하고 중복을 제거한다', () {
    final notice = _notice();
    final items = requirementActions({
      'requirements': [
        _actions.first,
        {'text': '근거 없는 항목', 'evidence': ''},
        {'text': '', 'evidence': '빈 항목 근거'},
      ],
    }, notice);
    expect(items, hasLength(4));
    expect(items.first['name'], '검증용 전공 변경 준비 1');
  });
  test('실패한 digest의 준비 항목은 사용하지 않는다', () {
    final notice = Notice(
      serverNotice(digest: {'status': 'failed', 'requirements': _actions}),
    );
    expect(
      requirementActions({
        'status': 'failed',
        'requirements': _actions,
      }, notice),
      isEmpty,
    );
  });
}

void _panelTest() {
  testWidgets('준비 API 404여도 공고의 근거 있는 준비 항목 4개를 표시한다', (tester) async {
    SharedPreferences.setMockInitialValues({});
    NoticeApi.client = MockClient((_) async => http.Response('{}', 404));
    addTearDown(() {
      NoticeApi.client.close();
      NoticeApi.client = http.Client();
    });
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(child: ApplyPanel(notice: _notice())),
        ),
      ),
    );
    await tester.pumpAndSettle();
    for (var i = 1; i <= 4; i++) {
      expect(find.text('검증용 전공 변경 준비 $i'), findsOneWidget);
      expect(find.text('근거: 예시 원문 근거 $i'), findsOneWidget);
    }
    expect(find.text('근거가 있는 준비 목록이 없어요. 원문을 확인해 주세요.'), findsNothing);
    expect(tester.takeException(), isNull);
  });
}

void _orderTest() {
  test('API 순서를 유지하고 2022·2023 지난 마감만 뒤로 보낸다', () {
    final c = FeedController()..sort = 'deadline';
    addTearDown(c.dispose);
    c.notices = [
      deadlineNotice('old2022', '2022-01-01'),
      deadlineNotice('unknown', null),
      deadlineNotice('later', '2099-01-03'),
      deadlineNotice('old2023', '2023-01-01'),
      deadlineNotice('earlier', '2099-01-02'),
    ];
    expect(c.visible.map((n) => n.id), [
      'unknown',
      'later',
      'earlier',
      'old2022',
      'old2023',
    ]);
  });
}

void _sourceTest() {
  test('SW사업단 출처도 다른 출처와 같은 공지 이름 형식을 사용한다', () {
    expect(Notice(serverNotice()).sourceName, 'SW사업단 공지사항');
    expect(
      Notice(
        serverNotice(
          extra: {
            'source': {
              'id': 'cs-notice',
              'name': 'SW 학사공지',
              'group': '소프트웨어융합대학',
            },
          },
        ),
      ).sourceName,
      'SW 학사공지',
    );
  });
}

Notice _notice() => Notice(
  serverNotice(id: 'server-action-four', digest: {'requirements': _actions}),
);
