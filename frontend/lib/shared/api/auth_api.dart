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
    ApiClient.token = res['token'] as String?;
    return res['id'] as String;
  }

  static Future<String> login(String nickname, String password) async {
    if (AppConfig.useMock) return MockAuth.login(nickname, password);
    final res = await ApiClient.post('/api/auth/login', {
      'nickname': nickname,
      'password': password,
    });
    ApiClient.token = res['token'] as String?;
    return res['id'] as String;
  }

  static Future<void> logout() async {
    if (!AppConfig.useMock) await ApiClient.post('/api/auth/logout', {});
    ApiClient.token = null;
  }

  // 서버에 있는 내 데이터를 모두 지운다.
  static Future<void> deleteMe() async {
    if (!AppConfig.useMock) await ApiClient.delete('/api/me');
    ApiClient.token = null;
  }

  static Future<void> recordConsent({required bool portfolio}) async {
    if (AppConfig.useMock) return;
    await ApiClient.post('/api/consent', {
      'type': portfolio ? 'portfolioAnalysis' : 'required',
      'version': AppConfig.consentVersion,
    });
  }
}
