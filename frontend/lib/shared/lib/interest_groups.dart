// 온보딩 관심 분야(Catalog.categories, PRD 10절)를 피드 카드(noticeGroups의 id)로 옮긴다.
// 분야 목록이나 카드가 바뀌면 이 표도 같이 고친다. 빠진 칸은 test/interest_seed_test.dart가 잡는다.
const interestGroupIds = <String, List<String>>{
  '학사': ['academic', 'graduation'],
  '장학': ['scholarship'],
  '공모전·행사': ['activity'],
  '채용·인턴': ['career'],
  '특강·교육': ['activity'],
  '국제교류': ['activity'],
  '봉사': ['activity'],
  '생활·시설': ['academic'],
  '시스템': ['other'],
  '기타': ['other'],
};

Set<String> feedGroupIdsFor(Iterable<String> categories) => <String>{
  for (final c in categories) ...?interestGroupIds[c],
};
