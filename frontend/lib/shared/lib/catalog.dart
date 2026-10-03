// 관심 분야는 서버가 내보내는 서비스 분류 6개(backend/app/ai/config/categories.json의 service).
// 태그는 PRD 6-1절 초안. 팀이 확정하면 여기만 고친다.
class Catalog {
  static const categories = ['학사·생활', '졸업', '장학', '취업', '행사·대외활동', '기타'];

  // AI 내부 분류(PRD 10절 10개)를 서비스 분류로 바꾸는 표. 서버 serviceMap과 같게 둔다.
  static const _legacyCategories = {
    '학사': '학사·생활',
    '공모전·행사': '행사·대외활동',
    '채용·인턴': '취업',
    '특강·교육': '행사·대외활동',
    '국제교류': '행사·대외활동',
    '봉사': '행사·대외활동',
    '생활·시설': '학사·생활',
    '시스템': '기타',
  };

  static Set<String> serviceCategories(Iterable<String> values) => {
        for (final v in values)
          if (categories.contains(_legacyCategories[v] ?? v))
            _legacyCategories[v] ?? v,
      };

  static const tags = [
    '개발',
    'AI·데이터',
    '디자인',
    '영상·콘텐츠',
    '마케팅·홍보',
    '기획·창업',
    '글쓰기',
    '외국어·글로벌',
    '금융·경제',
    '공공·정책',
    '환경·사회',
    '봉사',
    '연구',
    '스포츠·문화',
  ];

  static const majors = [
    '소프트웨어학부',
    '인공지능학부',
    '전자공학부',
    '기계공학부',
    '경영학부',
    '경제학과',
    '시각디자인학과',
    '공업디자인학과',
    '미디어·광고학부',
    '법학부',
    '국어국문학과',
    '영어영문학부',
  ];

  static const years = [1, 2, 3, 4];

  // 구독(Subscription.year)에 졸업생은 0으로 보낸다.
  static const graduateYear = 0;
  static const subscriptionYears = [...years, graduateYear];

  static String yearLabel(int year) =>
      year == graduateYear ? '졸업생' : '$year학년';
}
