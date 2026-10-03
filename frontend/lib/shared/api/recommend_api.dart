import 'package:kmu_notice/shared/lib/app_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';

import 'api_client.dart';

/// 공고마다 「될 가능성」과 추천 근거 한 줄. 서버가 AI 로 매긴다.
class Fit {
  const Fit(this.chance, this.reason);
  final int chance;
  final String reason;
}

class RecommendApi {
  /// 나의 상황(학과·학년·분야·태그)은 서버가 구독 설정에서 읽는다.
  /// 이름·연락처·학번은 보내지도 저장하지도 않는다 (지침서 8절).
  /// 로그인 전에는 맞춰 볼 내 정보가 없어서 묻지 않는다.
  static Future<Map<String, Fit>> fits(List<String> noticeIds) async {
    if (AppConfig.useMock || noticeIds.isEmpty || ApiClient.token == null) {
      return {};
    }
    final res = await ApiClient.post('/api/recommend', {'noticeIds': noticeIds});
    final items = res['items'];
    if (items is! List) return {};
    final result = <String, Fit>{};
    for (final raw in items.whereType<Map>()) {
      final item = mapValue(raw);
      final id = item['noticeId'];
      if (id is! String) continue;
      result[id] = Fit(
        (item['chance'] as num?)?.round() ?? 0,
        item['reason']?.toString() ?? '',
      );
    }
    return result;
  }
}
