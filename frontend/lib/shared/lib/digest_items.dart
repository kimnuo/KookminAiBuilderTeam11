import 'feed_config.dart';

List<Map<String, dynamic>> digestItems(dynamic raw, String field) {
  if (raw is! List) return [];
  return raw
      .whereType<Map>()
      .map((v) => Map<String, dynamic>.from(v))
      .where((v) => _text(v[field]) && _text(v['evidence']))
      .toList();
}

bool _text(dynamic value) => value is String && value.trim().isNotEmpty;

bool isApplicationPoint(Map<String, dynamic> point) {
  final label = point['label'];
  if (label is! String) return false;
  return RegExp(FeedConfig.applicationPointPattern).hasMatch(label);
}

String? digestApplication(Map<String, dynamic> digest) {
  final lines = digestItems(digest['keyPoints'], 'value')
      .where(isApplicationPoint)
      .map(
        (point) =>
            '${point['label']}: ${point['value']}\n근거: ${point['evidence']}',
      )
      .toSet()
      .toList();
  return lines.isEmpty ? null : lines.join('\n');
}
