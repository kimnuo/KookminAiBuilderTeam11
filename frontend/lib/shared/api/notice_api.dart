import 'dart:convert';

import 'package:http/http.dart' as http;

import 'package:kmu_notice/shared/lib/app_config.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';

import 'api_client.dart';
import 'notice_demo.dart';

class NoticeApi {
  static http.Client client = http.Client();
  static final Map<String, Future<Map<String, dynamic>>> _requirements = {};
  static Future<dynamic> _get(String path) async {
    final uri = Uri.parse('${AppConfig.apiBaseUrl}/api$path');
    final res = await client
        .get(
          uri,
          headers: {
            if (ApiClient.token != null)
              'Authorization': 'Bearer ${ApiClient.token}',
          },
        )
        .timeout(FeedConfig.requestTimeout);
    if (res.statusCode >= 400) {
      throw ApiException(res.statusCode, '공고를 불러오지 못했어요.');
    }
    return jsonDecode(utf8.decode(res.bodyBytes));
  }

  static List<dynamic> _items(dynamic data) => data is List
      ? data
      : (mapValue(data)['items'] ?? mapValue(data)['notices'] ?? []) as List;

  static Future<List<Notice>> feed(String sort) async {
    if (FeedConfig.demo) return NoticeDemo.feed();
    return _items(await _get('/feed?sort=$sort'))
        .map((j) => Notice(mapValue(j)))
        .toList();
  }

  static Future<Notice> detail(String id) async {
    if (!FeedConfig.demo) {
      return Notice(
        mapValue(await _get('/notices/${Uri.encodeComponent(id)}')),
      );
    }
    return (await NoticeDemo.feed()).firstWhere((n) => n.id == id);
  }

  static Future<Map<String, dynamic>> requirements(String id) async {
    final key = '${FeedConfig.demo}:$id';
    final request = _requirements.putIfAbsent(key, () async {
      if (FeedConfig.demo) {
        return mapValue((await NoticeDemo.read('requirements'))[id]);
      }
      return _serverRequirements(id);
    });
    try {
      return await request;
    } catch (_) {
      _requirements.remove(key);
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> _serverRequirements(String id) async {
    try {
      return mapValue(
        await _get('/notices/${Uri.encodeComponent(id)}/requirements'),
      );
    } on ApiException catch (error) {
      if (error.statusCode != 404) rethrow;
      return {'status': 'unavailable', 'fields': [], 'documents': []};
    }
  }
}
