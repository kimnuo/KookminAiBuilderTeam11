import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:kmu_notice/app/router.dart';
import 'package:kmu_notice/features/auth/welcome_page.dart';
import 'package:kmu_notice/features/profile/profile_analysis.dart';
import 'package:kmu_notice/shared/api/api_client.dart';
import 'package:kmu_notice/shared/lib/catalog.dart';
import 'package:kmu_notice/shared/lib/routes.dart';

import 'test_helpers.dart';

void main() {
  testWidgets('분석 결과 없이 결과 화면에 오면 PDF 고르기로 돌아간다', (tester) async {
    await pumpApp(tester);
    appRouter.go(Routes.portfolioReview);
    await tester.pumpAndSettle();

    expect(find.text('PDF 고르기'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('예시 결과일 때는 결과 화면에 표시한다', (tester) async {
    await pumpApp(tester);
    final analysis = ProfileAnalysis.fromJson({
      'skills': ['Python'],
    });
    appRouter.push(Routes.portfolioReview, extra: analysis);
    await tester.pumpAndSettle();

    expect(find.textContaining('데모용 예시 결과예요'), findsOneWidget);
  });

  test('로그인 토큰은 기기에 남아 다시 켜도 복구된다', () async {
    SharedPreferences.setMockInitialValues({});
    await ApiClient.setToken('t-123');
    ApiClient.token = null;
    await ApiClient.restoreToken();
    expect(ApiClient.token, 't-123');

    await ApiClient.setToken(null);
    await ApiClient.restoreToken();
    expect(ApiClient.token, isNull);
  });

  testWidgets('높이가 낮은 화면에서도 첫 화면이 넘치지 않고 스크롤된다', (tester) async {
    await pumpApp(tester);
    tester.view.physicalSize = const Size(1080, 1350);
    await tester.pumpAndSettle();
    appRouter.go(Routes.welcome);
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(
      find.descendant(
        of: find.byType(WelcomePage),
        matching: find.byType(SingleChildScrollView),
      ),
      findsOneWidget,
    );
  });

  testWidgets('관심 분야는 서버 분류 6개만 보여 준다', (tester) async {
    await pumpApp(tester);
    appRouter.push(Routes.onboardingInterests);
    await tester.pumpAndSettle();

    for (final c in Catalog.categories) {
      expect(find.text(c), findsOneWidget, reason: c);
    }
    expect(find.text('공모전·행사'), findsNothing);
  });
}
