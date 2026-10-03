class Notice {
  Notice(this.json);
  final Map<String, dynamic> json;
  String get id => json['id']?.toString() ?? '';
  String get title => json['title']?.toString() ?? '제목 없음';
  String get url => json['url']?.toString() ?? '';
  String get postedAt => json['postedAt']?.toString() ?? '';
  String get department => json['department']?.toString() ?? '';
  Map<String, dynamic> get source => mapValue(json['source']);
  String get sourceId => source['id']?.toString() ?? '';
  String get sourceName => source['name']?.toString() ?? '출처 미상';
  Map<String, dynamic> get ai =>
      mapValue(json['ai'])['status'] == 'done' ? mapValue(json['ai']) : {};
  String get aiStatus =>
      mapValue(json['ai'])['status']?.toString() ?? 'pending';
  List<String> get summary => strings(ai['summary']).take(3).toList();
  List<String> get categories => strings(ai['categories']);
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
