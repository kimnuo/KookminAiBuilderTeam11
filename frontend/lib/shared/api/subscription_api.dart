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
    await ApiClient.put('/api/subscriptions', {
      'major': major,
      'year': year,
      'categories': categories,
      'keywords': keywords,
      'tags': tags,
    });
  }

  static Future<void> saveTags(List<String> tags) async {
    if (AppConfig.useMock) return;
    await ApiClient.put('/api/subscriptions', {'tags': tags});
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
