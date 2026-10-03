import 'package:flutter_test/flutter_test.dart';

import 'package:kmu_notice/features/profile/profile_analysis.dart';

void main() {
  test('근거 없는 항목과 목록에 없는 태그는 버린다', () {
    final a = ProfileAnalysis.fromJson({
      'skills': ['Python'],
      'tags': ['개발', '없는태그'],
      'projects': [
        {'title': '근거 있음', 'evidence': '원문 문장'},
        {'title': '근거 없음', 'evidence': ''},
        {'title': '근거 필드 없음'},
      ],
      'awards': null,
    });

    expect(a.tags, ['개발']);
    expect(a.items.map((i) => i.title), ['근거 있음']);
  });
}
