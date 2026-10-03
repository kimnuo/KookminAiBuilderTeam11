import 'dart:convert';

import 'package:flutter/services.dart';

import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';

class NoticeDemo {
  static Future<dynamic> read(String file) async =>
      jsonDecode(await rootBundle.loadString('assets/demo/$file.json'));

  static Future<List<Notice>> feed() async {
    final files = await Future.wait(FeedConfig.demoFiles.map(read));
    final raw = files.expand((v) => v as List).map(mapValue).toList();
    final offset = koreaToday().difference(
      DateTime.parse('${raw.first['postedAt']}T00:00:00Z'),
    );
    return raw.map((j) => _shift(j, offset)).toList();
  }

  static Notice _shift(Map<String, dynamic> raw, Duration offset) {
    final j = Map<String, dynamic>.from(raw);
    final ai = mapValue(j['ai']);
    final d = mapValue(ai['deadline']);
    if (d['date'] != null) {
      final old = d['date'] as String;
      final date = DateTime.parse('${old}T00:00:00Z')
          .add(offset)
          .toIso8601String()
          .substring(0, 10);
      d['date'] = date;
      d['evidence'] = (d['evidence'] as String).replaceAll(old, date);
      ai['deadline'] = d;
    }
    j['postedAt'] = koreaToday().toIso8601String().substring(0, 10);
    j['ai'] = ai;
    return Notice(j);
  }
}
