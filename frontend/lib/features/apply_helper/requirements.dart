import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';

List<Map<String, dynamic>> requirementFields(Map<String, dynamic> data) =>
    _evidence(data['fields'])
        .where(
          (f) =>
              FeedConfig.fieldLabels.containsKey(f['key']) ||
              (f['key'] == 'other' &&
                  f['label'] is String &&
                  (f['label'] as String).trim().isNotEmpty),
        )
        .toList();
List<Map<String, dynamic>> requirementDocuments(Map<String, dynamic> data) =>
    _evidence(data['documents'])
        .where(
          (d) => d['name'] is String && (d['name'] as String).trim().isNotEmpty,
        )
        .toList();
List<Map<String, dynamic>> _evidence(dynamic raw) => raw is List
    ? raw
          .map(mapValue)
          .where(
            (item) =>
                item['evidence'] is String &&
                (item['evidence'] as String).trim().isNotEmpty,
          )
          .toList()
    : [];
