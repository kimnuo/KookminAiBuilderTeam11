import 'package:flutter/foundation.dart';

import 'package:kmu_notice/shared/lib/app_config.dart';
import 'api_client.dart';
import 'mock_auth.dart';

class AuthApi {
  // 로그인 상태. mock과 서버 모드 모두 여기서 켜고 끈다. 화면은 이 값을 듣고 다시 그린다.
  // 처음 읽을 때 main()의 ApiClient.restoreToken()이 되살린 토큰이 있으면 로그인 상태로 시작한다.
  static final loggedIn = ValueNotifier<bool>(ApiClient.token != null);
  static bool get isLoggedIn => loggedIn.value;

  // 닉네임이 이미 있으면 서버는 409를 준다.
  static Future<String> signup(String nickname, String password) async {
    final id = AppConfig.useMock
        ? await MockAuth.signup(nickname, password)
        : await _auth('/api/auth/signup', nickname, password);
    loggedIn.value = true;
    return id;
  }

  static Future<String> login(String nickname, String password) async {
    final id = AppConfig.useMock
        ? await MockAuth.login(nickname, password)
        : await _auth('/api/auth/login', nickname, password);
    loggedIn.value = true;
    return id;
  }

  static Future<String> _auth(
    String path,
    String nickname,
    String password,
  ) async {
    final res = await ApiClient.post(path, {
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
      loggedIn.value = false;
    }
  }

  // 서버에 있는 내 데이터를 모두 지운다. 실패하면 토큰을 남겨 다시 시도할 수 있게 한다.
  static Future<void> deleteMe() async {
    if (!AppConfig.useMock) await ApiClient.delete('/api/me');
    await ApiClient.setToken(null);
    loggedIn.value = false;
  }

  static Future<void> recordConsent({required bool portfolio}) async {
    if (AppConfig.useMock) return;
    await ApiClient.post('/api/consent', {
      'type': portfolio ? 'portfolioAnalysis' : 'required',
      'version': AppConfig.consentVersion,
    });
  }
}
