import 'api_client.dart';

// 백엔드 준비 전 데모용. 앱이 켜져 있는 동안 메모리에만 둔다.
class MockAuth {
  static final Map<String, String> _users = {};

  static Future<String> signup(String nickname, String password) async {
    await Future.delayed(const Duration(milliseconds: 400));
    if (_users.containsKey(nickname)) {
      throw ApiException(409, '이미 사용 중인 닉네임');
    }
    _users[nickname] = password;
    return 'u_$nickname';
  }

  static Future<String> login(String nickname, String password) async {
    await Future.delayed(const Duration(milliseconds: 400));
    if (_users[nickname] != password) {
      throw ApiException(401, '닉네임 또는 비밀번호 불일치');
    }
    return 'u_$nickname';
  }
}
