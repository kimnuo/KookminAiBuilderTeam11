import 'feed_config.dart';

String? noticeMediaUrl(dynamic value, dynamic base) {
  if (value is! String || value.trim().isEmpty) return null;
  final uri = Uri.tryParse(value.trim());
  final origin = base is String ? Uri.tryParse(base) : null;
  final resolved = uri == null ? null : origin?.resolveUri(uri) ?? uri;
  if (resolved == null ||
      !{'http', 'https'}.contains(resolved.scheme) ||
      resolved.host.isEmpty ||
      resolved.userInfo.isNotEmpty) {
    return null;
  }
  return resolved.toString();
}

List<Map<String, dynamic>> noticePosters(
  Map<String, dynamic> preview,
  List<Map<String, dynamic>> attachments,
  String base,
) {
  final raw = preview['poster'];
  final poster = raw is Map
      ? Map<String, dynamic>.from(raw)
      : <String, dynamic>{};
  final urls = <String>{};
  final result = <Map<String, dynamic>>[];
  if (poster['asset'] is String && (poster['asset'] as String).isNotEmpty) {
    result.add(poster);
  }
  for (final item in [poster, ...attachments]) {
    final url = noticeMediaUrl(item['url'], base);
    if (url == null) continue;
    if (item != poster && !_isImage(item, url)) continue;
    if (!urls.add(url)) continue;
    result.add({
      ...item,
      'url': url,
      'alt': item['alt'] ?? item['name'] ?? '공고 포스터',
    });
  }
  return result;
}

bool _isImage(Map<String, dynamic> file, String url) {
  final type = '${file['type'] ?? ''}'.toLowerCase().replaceFirst('image/', '');
  final ext = Uri.parse(url).path.split('.').last.toLowerCase();
  final name = '${file['name'] ?? ''}'.split('.').last.toLowerCase();
  return FeedConfig.posterImageTypes.contains(type) ||
      FeedConfig.posterImageTypes.contains(ext) ||
      FeedConfig.posterImageTypes.contains(name);
}
