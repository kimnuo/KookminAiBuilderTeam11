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

// 지원 준비 API(fields/documents)와 공고 API(digest.requirements)를 함께 읽는다.
List<Map<String, dynamic>> requirementActions(
  Map<String, dynamic> data,
  Notice notice,
) {
  final digest = mapValue(data['digest']);
  final direct = data['status'] == 'failed'
      ? <Map<String, dynamic>>[]
      : _evidence(data['requirements']);
  final items = <Map<String, dynamic>>[
    ...direct,
    if (digest['status'] == 'done') ..._evidence(digest['requirements']),
    ...notice.requiredActions,
  ];
  final seen = <String>{};
  return items
      .where((item) {
        final text = item['text'];
        return text is String &&
            text.trim().isNotEmpty &&
            seen.add(text.trim());
      })
      .map((item) => <String, dynamic>{...item, 'name': item['text']})
      .toList();
}
