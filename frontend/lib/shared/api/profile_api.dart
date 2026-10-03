import 'package:kmu_notice/shared/lib/app_config.dart';
import 'api_client.dart';

class ProfileApi {
  // 전화번호·이메일·학번을 가린 글만 보낸다. 서버는 저장하거나 로그에 남기지 않는다.
  static Future<Map<String, dynamic>> analyze(String maskedText) async {
    if (AppConfig.useMock) {
      await Future.delayed(const Duration(milliseconds: 900));
      return _mockResult;
    }
    return ApiClient.post('/api/profile/analyze', {'text': maskedText});
  }

  // 화면 개발용 형식 예시. 실제 추출 결과가 아니다.
  static const _mockResult = {
    'skills': ['Python', 'Figma'],
    'tags': ['개발', 'AI·데이터'],
    'projects': [
      {
        'title': '캠퍼스 분실물 찾기 앱',
        'role': '프론트엔드',
        'period': '2025.03~2025.06',
        'evidence': '캠퍼스 분실물 찾기 앱 개발 (프론트엔드 담당)',
      },
    ],
    'awards': [
      {
        'title': '교내 해커톤 우수상',
        'date': '2025.11',
        'evidence': '2025 교내 해커톤 우수상 수상',
      },
    ],
    'activities': [
      {
        'title': '프로그래밍 동아리',
        'period': '2024~',
        'evidence': '프로그래밍 동아리 부원으로 활동',
      },
    ],
  };
}
