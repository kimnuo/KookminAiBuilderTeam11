import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

// PRD 10절 Profile의 지원 정보. 이 기기에만 저장하고 서버·AI로 보내지 않는다.
// 지원 준비 패널(apply-helper)도 이 값을 읽는다.
class ApplicantInfo {
  static const keys = [
    'name',
    'phone',
    'email',
    'studentId',
    'school',
    'major',
    'year',
    'birthDate',
    'portfolioUrl',
  ];

  ApplicantInfo([Map<String, String?>? values])
      : values = {for (final k in keys) k: values?[k]};

  final Map<String, String?> values;

  String? operator [](String key) => values[key];
}

class ApplicantStore {
  static const _key = 'profile.applicant';

  static Future<ApplicantInfo> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null) return ApplicantInfo({'school': '국민대학교'});
    final map = Map<String, dynamic>.from(jsonDecode(raw) as Map);
    return ApplicantInfo(map.map((k, v) => MapEntry(k, v as String?)));
  }

  static Future<void> save(ApplicantInfo info) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, jsonEncode(info.values));
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
