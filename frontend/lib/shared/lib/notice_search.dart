import 'feed_config.dart';
import 'notice.dart';

String normalizeSearch(String value) {
  var text = String.fromCharCodes(
    value.runes.map((r) => r >= 0xFF01 && r <= 0xFF5E ? r - 0xFEE0 : r),
  );
  text = text.toLowerCase().replaceAll(RegExp(r'[^a-z0-9가-힣ㄱ-ㅎㅏ-ㅣ]'), '');
  for (final entry in FeedConfig.aliases.entries) {
    text = text.replaceAll(entry.key, entry.value);
  }
  return text;
}

List<NoticeGroup> groupsFor(Notice n) {
  final source = normalizeSearch(
    '${n.sourceId} ${n.sourceName} ${n.department} ${n.url}',
  );
  final title = normalizeSearch(n.title);
  final matched = noticeGroups.where((g) {
    if (g.exclude.any((w) => title.contains(normalizeSearch(w)))) return false;
    return g.sources.any((w) => source.contains(normalizeSearch(w))) ||
        g.categories.any(n.categories.contains) ||
        g.keywords.any((w) => title.contains(normalizeSearch(w)));
  }).toList();
  return matched.isEmpty ? [noticeGroups.last] : matched;
}

bool matchesSearch(Notice n, String query) {
  final text = normalizeSearch(
    [
      n.title,
      n.json['originalTitle']?.toString() ?? '',
      n.sourceName,
      n.department,
      n.audience ?? '',
      n.apply ?? '',
      ...n.summary,
      ...n.categories,
      ...n.tags,
      ...groupsFor(n).map((g) => g.label),
    ].join(' '),
  );
  return query
      .trim()
      .split(RegExp(r'\s+'))
      .map(normalizeSearch)
      .where((w) => w.isNotEmpty)
      .every(text.contains);
}
