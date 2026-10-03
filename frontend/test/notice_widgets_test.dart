import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:kmu_notice/features/apply_helper/apply_panel.dart';
import 'package:kmu_notice/features/notice/notice_content.dart';
import 'package:kmu_notice/features/notice/poster_preview.dart';
import 'package:kmu_notice/shared/api/notice_api.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'support/notice_fixture.dart';

void main() {
  _detailTests();
  _posterTest();
  _preparationTests();
}

void _detailTests() {
  testWidgets('실서버 신청 방법·주요 내역·필수 사항과 근거 표시', (tester) async {
    final n = Notice(
      serverNotice(
        digest: {
          'keyPoints': [
            {'label': '신청 방법', 'value': '온라인 신청', 'evidence': '검증용 신청 근거'},
            {'label': '장소', 'value': '예시 강의실', 'evidence': '검증용 장소 근거'},
          ],
          'requirements': [
            {'text': '예시 신청서 제출', 'evidence': '검증용 제출 근거'},
          ],
        },
      ),
    );
    await _pump(
      tester,
      NoticeContent(notice: n, preparation: const SizedBox()),
    );
    expect(find.text('신청 방법'), findsOneWidget);
    expect(find.textContaining('검증용 신청 근거'), findsOneWidget);
    expect(find.text('주요 내역'), findsOneWidget);
    expect(find.text('필수 사항'), findsOneWidget);
  });
  testWidgets('분석 실패 시 요약·신청 방법·준비 패널을 숨긴다', (tester) async {
    final n = Notice(serverNotice(digest: {'status': 'failed'}));
    await _pump(
      tester,
      NoticeContent(notice: n, preparation: const Text('준비 패널')),
    );
    expect(find.text('AI 분석을 완료하지 못했어요.'), findsOneWidget);
    expect(find.text('핵심 요약'), findsNothing);
    expect(find.text('준비 패널'), findsNothing);
  });
}

void _posterTest() {
  testWidgets('데모 포스터를 확대하고 닫는다', (tester) async {
    await _pump(
      tester,
      const SizedBox(
        width: 220,
        child: PosterPreview(
          poster: {
            'asset': 'assets/demo/media/ai-challenge-poster.png',
            'alt': '예시 포스터',
          },
        ),
      ),
    );
    await tester.tap(find.text('포스터 확대'));
    await tester.pumpAndSettle();
    expect(find.byType(Dialog), findsOneWidget);
    await tester.tap(find.byTooltip('포스터 닫기'));
    await tester.pumpAndSettle();
    expect(find.byType(Dialog), findsNothing);
  });
}

void _preparationTests() {
  testWidgets('404 준비 API는 공고 원문 안내로 표시', (tester) async {
    SharedPreferences.setMockInitialValues({});
    NoticeApi.client = MockClient((_) async => http.Response('{}', 404));
    addTearDown(() {
      NoticeApi.client.close();
      NoticeApi.client = http.Client();
    });
    await _pump(
      tester,
      ApplyPanel(notice: Notice(serverNotice(id: 'widget-404'))),
    );
    expect(find.text('필요한 항목은 공고의 필수 사항과 원문에서 확인해 주세요.'), findsOneWidget);
    expect(find.text('내 지원 정보 수정'), findsOneWidget);
    expect(find.textContaining('불러오지 못했어요'), findsNothing);
  });
}

Future<void> _pump(WidgetTester tester, Widget child) async {
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(
          child: Padding(padding: const EdgeInsets.all(16), child: child),
        ),
      ),
    ),
  );
  await tester.pumpAndSettle();
}
