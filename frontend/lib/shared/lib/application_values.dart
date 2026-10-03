import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import 'applicant_store.dart';
import 'feed_config.dart';
import 'notice.dart';

import 'package:kmu_notice/shared/api/notice_demo.dart';

Future<Map<String, String>> applicationValues() async {
  if (FeedConfig.demo) {
    return _flatten(mapValue(await NoticeDemo.read('profile')));
  }
  final prefs = await SharedPreferences.getInstance();
  final raw = prefs.getString('profile.history');
  final history = raw == null ? <String, dynamic>{} : mapValue(jsonDecode(raw));
  return _flatten({
    ...((await ApplicantStore.load()).values),
    'history': history,
  });
}

Map<String, String> _flatten(Map<String, dynamic> profile) {
  final history = mapValue(profile['history']);
  return {
    for (final key in FeedConfig.fieldLabels.keys)
      key: _display(profile[key] ?? history[key]),
  };
}

String _display(dynamic value) {
  if (value == null) return '';
  if (value is List) {
    return value.map(_display).where((s) => s.isNotEmpty).join('\n');
  }
  if (value is Map) {
    return ['name', 'title', 'period', 'detail']
        .map((k) => value[k]?.toString() ?? '')
        .where((s) => s.isNotEmpty)
        .join(' · ');
  }
  return value.toString();
}
