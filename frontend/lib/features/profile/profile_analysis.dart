import 'package:kmu_notice/shared/lib/catalog.dart';

class AnalysisItem {
  AnalysisItem(this.kind, this.title, this.detail, this.evidence);
  final String kind;
  final String title;
  final String? detail;
  final String? evidence;
  bool keep = true;
}

// extractProfile 결과(PRD 6-1절). 근거 문장이 없는 항목과 목록에 없는 태그는 버린다.
class ProfileAnalysis {
  ProfileAnalysis(this.skills, this.tags, this.items);

  final List<String> skills;
  final List<String> tags;
  final List<AnalysisItem> items;

  bool get isEmpty => skills.isEmpty && tags.isEmpty && items.isEmpty;

  factory ProfileAnalysis.fromJson(Map<String, dynamic> j) {
    final items = [
      ..._items(j['projects'], 'projects', 'period'),
      ..._items(j['awards'], 'awards', 'date'),
      ..._items(j['activities'], 'activities', 'period'),
    ];
    return ProfileAnalysis(
      List<String>.from(j['skills'] ?? const []),
      List<String>.from(j['tags'] ?? const [])
          .where(Catalog.tags.contains)
          .toList(),
      items,
    );
  }

  static Iterable<AnalysisItem> _items(dynamic raw, String kind, String key) {
    final list = (raw as List? ?? const []).cast<Map>();
    return list
        .where((e) => (e['evidence'] as String? ?? '').trim().isNotEmpty)
        .where((e) => (e['title'] as String? ?? '').trim().isNotEmpty)
        .map((e) => AnalysisItem(
              kind,
              e['title'] as String,
              e[key] as String?,
              e['evidence'] as String,
            ));
  }
}
