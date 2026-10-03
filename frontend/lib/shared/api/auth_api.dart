import 'package:kmu_notice/shared/lib/app_config.dart';
import 'api_client.dart';
import 'mock_auth.dart';

class AuthApi {
  // 닉네임이 이미 있으면 서버는 409를 준다.
  static Future<String> signup(String nickname, String password) async {
    if (AppConfig.useMock) return MockAuth.signup(nickname, password);
    final res = await ApiClient.post('/api/auth/signup', {
      'nickname': nickname,
      'password': password,
    });
    await ApiClient.setToken(res['token'] as String?);
    return res['id'] as String;
  }

  static Future<String> login(String nickname, String password) async {
    if (AppConfig.useMock) return MockAuth.login(nickname, password);
    final res = await ApiClient.post('/api/auth/login', {
      'nickname': nickname,
      'password': password,
    });
    await ApiClient.setToken(res['token'] as String?);
    return res['id'] as String;
  }

  // 서버 로그아웃이 실패해도 이 기기의 토큰은 지운다.
  static Future<void> logout() async {
    try {
      if (!AppConfig.useMock) await ApiClient.post('/api/auth/logout', {});
    } finally {
      await ApiClient.setToken(null);
    }
  }

  // 서버에 있는 내 데이터를 모두 지운다. 실패하면 토큰을 남겨 다시 시도할 수 있게 한다.
  static Future<void> deleteMe() async {
    if (!AppConfig.useMock) await ApiClient.delete('/api/me');
    await ApiClient.setToken(null);
  }

  static Future<void> recordConsent({required bool portfolio}) async {
    if (AppConfig.useMock) return;
    await ApiClient.post('/api/consent', {
      'type': portfolio ? 'portfolioAnalysis' : 'required',
      'version': AppConfig.consentVersion,
    });
  }
}
