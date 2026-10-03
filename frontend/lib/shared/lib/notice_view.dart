import 'digest_items.dart';

Map<String, dynamic> noticeView(Map<String, dynamic> raw) {
  if (raw['digest'] is! Map) return raw;
  final digest = Map<String, dynamic>.from(raw['digest']);
  final done = digest['status'] == 'done';
  return {
    ...raw,
    'title':
        done &&
            digest['title'] is String &&
            (digest['title'] as String).trim().isNotEmpty
        ? digest['title']
        : raw['originalTitle'],
    'ai': {
      'status': digest['status'],
      'categories': raw['categories'] ?? [],
      'tags': digest['tags'] ?? [],
      'summary': digest['summary'] is String ? [digest['summary']] : [],
      'deadline': digest['deadline'],
      'audience': digest['audience'],
      'apply': done ? digestApplication(digest) : null,
    },
  };
}
