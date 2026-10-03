import 'package:flutter/material.dart';

class FeedConfig {
  static const requestTimeout = Duration(seconds: 20);
  static const pageSize = 8;
  static const detailDialogWidth = 820.0;
  static const detailDialogHeight = 720.0;
  static const detailDialogRatio = .82;
  static const previewCount = 3;
  static const previewRowHeight = 42.0;
  static const compactPreviewRowHeight = 28.0;
  static const sortOptions = {'recommend': '추천 순', 'deadline': '마감 임박 순'};
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
    'academic',
    '학사·생활',
    Icons.school_rounded,
    Color(0xFF3182F6),
    categories: ['학사·생활'],
  ),
  NoticeGroup(
    'graduation',
    '졸업',
    Icons.school_rounded,
    Color(0xFF7355DC),
    categories: ['졸업'],
  ),
  NoticeGroup(
    'scholarship',
    '장학',
    Icons.savings_rounded,
    Color(0xFF31A875),
    categories: ['장학'],
  ),
  NoticeGroup(
    'career',
    '취업',
    Icons.work_rounded,
    Color(0xFF5979BE),
    categories: ['취업'],
  ),
  NoticeGroup(
    'activity',
    '행사·대외활동',
    Icons.emoji_events_rounded,
    Color(0xFFE69B23),
    categories: ['행사·대외활동'],
  ),
  NoticeGroup(
    'other',
    '기타',
    Icons.widgets_rounded,
    Color(0xFF80909F),
    categories: ['기타'],
  ),
];
