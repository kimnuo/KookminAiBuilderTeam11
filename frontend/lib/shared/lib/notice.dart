import 'notice_view.dart';
import 'notice_media_data.dart';
import 'digest_items.dart';

class Notice {
  Notice(Map<String, dynamic> raw) : json = noticeView(raw);
  final Map<String, dynamic> json;
  String get id => json['id']?.toString() ?? '';
  String get title => json['title']?.toString() ?? '제목 없음';
  String get url => json['url']?.toString() ?? '';
  Map<String, dynamic> get previewMedia => mapValue(json['previewMedia']);
  List<Map<String, dynamic>> get posters =>
      noticePosters(previewMedia, attachments, url);
  List<Map<String, dynamic>> get attachments =>
      [...mapList(previewMedia['files']), ...mapList(json['attachments'])]
          .map(
            (file) => file['asset'] is String
                ? file
                : {...file, 'url': noticeMediaUrl(file['url'], url)},
          )
          .toList();
  Map<String, dynamic> get digest => mapValue(json['digest']);
  List<Map<String, dynamic>> get keyPoints => ai.isEmpty
      ? []
      : digestItems(digest['keyPoints'], 'value')
            .where(
              (p) =>
                  p['label'] is String &&
                  (p['label'] as String).trim().isNotEmpty,
            )
            .toList();
  List<Map<String, dynamic>> get requiredActions =>
      ai.isEmpty ? [] : digestItems(digest['requirements'], 'text');
  String get postedAt => json['postedAt']?.toString() ?? '';
  String get department => json['department']?.toString() ?? '';
  Map<String, dynamic> get source => mapValue(json['source']);
  String get sourceId => source['id']?.toString() ?? '';
  String get sourceName {
    final name = source['name']?.toString() ?? '출처 미상';
    final group = source['group']?.toString();
    return name == '공지사항' && group != null ? '$group · $name' : name;
  }

  Map<String, dynamic> get ai =>
      mapValue(json['ai'])['status'] == 'done' ? mapValue(json['ai']) : {};
  String get aiStatus =>
      mapValue(json['ai'])['status']?.toString() ?? 'pending';
  List<String> get summary => strings(ai['summary']).take(3).toList();
  List<String> get categories =>
      strings(json['categories'] ?? ai['categories']);
  List<String> get tags => strings(ai['tags']);
  String? get audience => mapValue(ai['audience'])['text']?.toString();
  String? get apply => ai['apply']?.toString();
  List<String> get reasons {
    if (ai.isEmpty) return [];
    final raw = json['recommendationReasons'] ?? json['reasons'] ?? [];
    return (raw is List ? raw : [raw])
        .map((v) => v is String ? v : mapValue(v)['text']?.toString() ?? '')
        .where((v) => v.trim().isNotEmpty)
        .toList();
  }
}

Map<String, dynamic> mapValue(dynamic value) =>
    value is Map ? Map<String, dynamic>.from(value) : {};
List<String> strings(dynamic value) => value is List
    ? value.whereType<String>().where((s) => s.trim().isNotEmpty).toList()
    : [];

List<Map<String, dynamic>> mapList(dynamic value) =>
    value is List ? value.whereType<Map>().map(mapValue).toList() : [];
