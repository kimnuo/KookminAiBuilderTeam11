import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:kmu_notice/app/router.dart';
import 'package:kmu_notice/features/onboarding/onboarding_draft.dart';
import 'package:kmu_notice/features/profile/profile_store.dart';
import 'package:kmu_notice/shared/lib/catalog.dart';
import 'package:kmu_notice/shared/lib/routes.dart';

import 'test_helpers.dart';

void main() {
  testWidgets('가입부터 이력 저장까지 한 번에 지나간다', (tester) async {
    await pumpApp(tester);

    await tapText(tester, '시작하기');
    await fillFields(tester, ['flow_user', 'testpass123']);
    await tapText(tester, '가입하기');

    await tapText(tester, '[필수] 개인정보 수집·이용에 동의해요');
    await tapText(tester, '동의하고 계속하기');

    await tapText(tester, '3학년');
    await tapText(tester, '소프트웨어학부');
    await tapText(tester, '다음');

    await tester.enterText(find.byType(TextField).first, 'AI 공모전이랑 장학금');
    await tapText(tester, 'AI로 고르기');
    expect(find.text('2개 분야 받기'), findsOneWidget);
    await tapText(tester, '2개 분야 받기');

    await tapText(tester, 'AI·데이터');
    await tapText(tester, '저장하고 피드 보기');
    expect(find.text('크노'), findsOneWidget);
    expect(find.text('모든 카테고리'), findsOneWidget);

    final saved = await ProfileStore.load();
    expect(saved.tags, ['AI·데이터']);
  });

  testWidgets('졸업생을 고르면 학년 값 0으로 넘어간다', (tester) async {
    await pumpApp(tester);
    appRouter.push(Routes.onboardingMajor);
    await tester.pumpAndSettle();

    await tapText(tester, '졸업생');
    await tapText(tester, '소프트웨어학부');
    await tapText(tester, '다음');

    expect(OnboardingDraft.year, Catalog.graduateYear);
    expect(find.text('어떤 소식을\n받아 볼까요?'), findsOneWidget);
  });
}
