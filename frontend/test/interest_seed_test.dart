import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:kmu_notice/app/router.dart';
import 'package:kmu_notice/features/feed/feed_controller.dart';
import 'package:kmu_notice/shared/api/notice_api.dart';
import 'package:kmu_notice/shared/lib/catalog.dart';
import 'package:kmu_notice/shared/lib/interest_groups.dart';
import 'package:kmu_notice/shared/lib/interest_store.dart';
import 'package:kmu_notice/shared/lib/routes.dart';

import 'test_helpers.dart';

void main() {
  test('모든 관심 분야가 실제 피드 카드로 이어진다', () {
    for (final c in Catalog.categories) {
      expect(feedGroupIdsFor([c]), hasLength(1), reason: c);
    }
  });

  test('예전 분야 이름도 서비스 분류로 바꿔서 이어진다', () {
    expect(feedGroupIdsFor(['채용·인턴', '공모전·행사', '시스템']), {
      'career',
      'activity',
      'other',
    });
  });

  test('온보딩에서 고른 분야가 피드 첫 선택값이 되고 한 번만 깔린다', () async {
    SharedPreferences.setMockInitialValues({});
    NoticeApi.client = MockClient((_) async => http.Response('[]', 200));
    addTearDown(() => NoticeApi.client = http.Client());
    await InterestStore.save(['장학', '채용·인턴', '없는 분야']);

    final feed = FeedController();
    await feed.load();
    expect(feed.selected, {'scholarship', 'career'});

    feed.toggle('career');
    await feed.load();
    expect(feed.selected, {'scholarship'});
  });

  testWidgets('관심 분야를 다시 고르면 저장해 둔 분야가 켜져 있다', (tester) async {
    await pumpApp(tester);
    await InterestStore.save(['장학']);

    appRouter.push(Routes.onboardingInterests);
    await tester.pumpAndSettle();

    expect(find.text('1개 분야 받기'), findsOneWidget);
  });
}
