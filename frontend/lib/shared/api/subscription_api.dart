import 'package:kmu_notice/shared/lib/app_config.dart';
import 'api_client.dart';

class SubscriptionApi {
  // 서버로는 학과·학년·분야·태그만 보낸다. 이름·연락처·학번은 넣지 않는다.
  static Future<void> save({
    required String major,
    required int year,
    required List<String> categories,
    List<String> keywords = const [],
    List<String> tags = const [],
  }) async {
    if (AppConfig.useMock) {
      await Future.delayed(const Duration(milliseconds: 300));
      return;
    }
    await _put({
      'major': major,
      'year': year,
      'categories': categories,
      'keywords': keywords,
      'tags': tags,
    });
  }

  static Future<void> saveTags(List<String> tags) async {
    if (AppConfig.useMock) return;
    await _put({'tags': tags});
  }

  // 서버 PUT /api/subscriptions는 로그인 토큰이 있어야 받는다. 실패해도 온보딩을 막지 않는다.
  // 관심 분야는 InterestStore에 먼저 저장하므로 피드는 그 값으로 동작한다.
  static Future<void> _put(Map<String, dynamic> body) async {
    try {
      await ApiClient.put('/api/subscriptions', body);
    } catch (_) {
      // 일부러 넘긴다. 서버 구독 API가 생기면 실패 안내를 다시 정한다.
    }
  }

  static Future<Map<String, dynamic>> parse(String text) async {
    if (AppConfig.useMock) {
      await Future.delayed(const Duration(milliseconds: 600));
      return {
        'categories': ['공모전·행사', '장학'],
        'keywords': ['AI'],
        'year': null,
      };
    }
    return ApiClient.post('/api/subscriptions/parse', {'text': text});
  }
}
