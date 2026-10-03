import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:kmu_notice/app/router.dart';
import 'package:kmu_notice/features/profile/profile_analysis.dart';
import 'package:kmu_notice/features/profile/profile_store.dart';
import 'package:kmu_notice/shared/lib/applicant_store.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'test_helpers.dart';

void main() {
  testWidgets('검토에서 체크를 끈 항목은 저장하지 않는다', (tester) async {
    await pumpApp(tester);
    final analysis = ProfileAnalysis.fromJson({
      'skills': ['Python'],
      'tags': ['개발'],
      'projects': [
        {'title': '남길 프로젝트', 'evidence': '근거 1'},
        {'title': '뺄 프로젝트', 'evidence': '근거 2'},
      ],
    });
    appRouter.push(Routes.portfolioReview, extra: analysis);
    await tester.pumpAndSettle();

    await tapText(tester, '뺄 프로젝트');
    await tapText(tester, '내 이력에 저장');

    final h = await ProfileStore.load();
    expect(h.tags, ['개발']);
    expect(h.skills, ['Python']);
    expect(h.projects.map((e) => e['title']), ['남길 프로젝트']);
  });

  testWidgets('지원 정보는 기기에 저장되고 빈 칸은 null이다', (tester) async {
    await pumpApp(tester);
    appRouter.push(Routes.applicantInfo);
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextField).at(0), '김예시');
    await tapText(tester, '3학년');
    await tapText(tester, '저장');

    final info = await ApplicantStore.load();
    expect(info['name'], '김예시');
    expect(info['year'], '3');
    expect(info['school'], '국민대학교');
    expect(info['phone'], isNull);
  });

  testWidgets('탈퇴하면 기기의 이력과 지원 정보도 지운다', (tester) async {
    await pumpApp(tester);
    await ProfileStore.save(ProfileHistory(tags: ['개발']));
    await ApplicantStore.save(ApplicantInfo({'name': '김예시'}));

    appRouter.push(Routes.settings);
    await tester.pumpAndSettle();
    await tapText(tester, '탈퇴하기');
    await tapText(tester, '탈퇴');

    expect(find.text('시작하기'), findsOneWidget);
    expect((await ProfileStore.load()).tags, isEmpty);
    expect((await ApplicantStore.load())['name'], isNull);
  });
}
