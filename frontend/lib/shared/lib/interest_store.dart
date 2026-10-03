import 'package:shared_preferences/shared_preferences.dart';

// 온보딩에서 고른 관심 분야(Catalog.categories). 이 기기에 저장하고 피드 첫 선택값으로 쓴다.
// 서버 구독 저장(SubscriptionApi.save)이 실패해도 이 값은 남는다.
class InterestStore {
  static const _key = 'subscription.categories';

  static Future<List<String>> load() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(_key) ?? [];
  }

  static Future<void> save(List<String> categories) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_key, categories);
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
