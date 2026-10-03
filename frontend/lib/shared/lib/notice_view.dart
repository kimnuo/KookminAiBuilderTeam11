Map<String, dynamic> noticeView(Map<String, dynamic> raw) {
  if (raw['digest'] is! Map) return raw;
  final digest = Map<String, dynamic>.from(raw['digest']);
  final done = digest['status'] == 'done';
  return {
    ...raw,
    'title': done
        ? (digest['title'] ?? raw['originalTitle'])
        : raw['originalTitle'],
    'ai': {
      'status': digest['status'],
      'categories': raw['categories'] ?? [],
      'tags': raw['matchedTags'] ?? [],
      'summary': digest['summary'] is String ? [digest['summary']] : [],
      'deadline': digest['deadline'],
      'audience': digest['audience'],
      'apply': null,
    },
  };
}
