import 'package:flutter/material.dart';

class FeedConfig {
  static const requestTimeout = Duration(seconds: 20);
  static const pageSize = 8;
  static const koreaOffset = Duration(hours: 9);
  static const demoFiles = ['notices', 'more-notices', 'campus-notices'];
  static const fieldLabels = {
    'name': '이름',
    'phone': '연락처',
    'email': '이메일',
    'studentId': '학번',
    'school': '학교',
    'major': '학과',
    'year': '학년',
    'birthDate': '생년월일',
    'portfolioUrl': '포트폴리오 링크',
    'certificates': '자격증',
    'awards': '수상',
    'activities': '활동',
  };
  static const aliases = {
    '소프트웨어융합대학': 'sw대학',
    '소프트웨어대학': 'sw대학',
    '소프트웨어중심대학사업단': 'sw사업단',
    'sw중심대학사업단': 'sw사업단',
    '소프트웨어중심대학': 'sw사업단',
    'sw중심대학': 'sw사업단',
    '국민대학교': '국민대',
  };
  static bool get demo =>
      Uri.base.queryParameters['demo'] == '1' ||
      Uri.tryParse(Uri.base.fragment)?.queryParameters['demo'] == '1';
}

class NoticeGroup {
  const NoticeGroup(
    this.id,
    this.label,
    this.icon,
    this.color, {
    this.sources = const [],
    this.categories = const [],
    this.keywords = const [],
    this.exclude = const [],
  });
  final String id, label;
  final IconData icon;
  final Color color;
  final List<String> sources, categories, keywords, exclude;
}

const noticeGroups = [
  NoticeGroup(
    'sw-college',
    '국민대 SW대학',
    Icons.school_rounded,
    Color(0xFF3182F6),
    sources: ['cs.kookmin.ac.kr', 'SW대학', '소프트웨어융합대학', '소프트웨어대학'],
  ),
  NoticeGroup(
    'sw-project',
    'SW사업단',
    Icons.auto_awesome_rounded,
    Color(0xFF7355DC),
    sources: ['SW사업단', '소프트웨어중심대학', 'SW중심대학', 'SW교육센터'],
  ),
  NoticeGroup(
    'competition',
    '공모전',
    Icons.emoji_events_rounded,
    Color(0xFFE69B23),
    categories: ['공모전·행사'],
    keywords: ['공모전', '경진대회'],
    exclude: ['서포터즈', '홍보대사', '대외활동', '기자단'],
  ),
  NoticeGroup(
    'volunteer',
    '봉사활동',
    Icons.volunteer_activism_rounded,
    Color(0xFFDE6484),
    categories: ['봉사'],
    keywords: ['봉사활동', '봉사단'],
  ),
  NoticeGroup(
    'activity',
    '대외활동',
    Icons.explore_rounded,
    Color(0xFF27A1A5),
    keywords: ['대외활동', '서포터즈', '홍보대사', '기자단'],
  ),
  NoticeGroup(
    'scholarship',
    '장학',
    Icons.savings_rounded,
    Color(0xFF31A875),
    categories: ['장학'],
    keywords: ['장학금', '장학생'],
  ),
  NoticeGroup(
    'career',
    '취업·인턴',
    Icons.work_rounded,
    Color(0xFF5979BE),
    categories: ['채용·인턴'],
    keywords: ['인턴', '채용'],
  ),
  NoticeGroup(
    'education',
    '학사·교육',
    Icons.menu_book_rounded,
    Color(0xFF7E77BD),
    categories: ['학사', '특강·교육'],
  ),
  NoticeGroup(
    'global',
    '국제교류',
    Icons.public_rounded,
    Color(0xFF43A6CE),
    categories: ['국제교류'],
  ),
  NoticeGroup('other', '기타 소식', Icons.widgets_rounded, Color(0xFF80909F)),
];
