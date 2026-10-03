import 'package:kmu_notice/shared/lib/notice.dart';

Map<String, dynamic> serverNotice({
  String id = 'review-notice',
  Map<String, dynamic> digest = const {},
  Map<String, dynamic> extra = const {},
}) => {
  'id': id,
  'originalTitle': '검증용 공고 원 제목',
  'url': 'https://example.com/notices/1',
  'postedAt': '2026-10-03',
  'source': {'id': 'sw-notice', 'name': '공지사항', 'group': 'SW중심대학사업단'},
  'categories': ['행사·대외활동'],
  'attachments': [],
  'digest': {
    'status': 'done',
    'title': '검증용 공고 요약 제목',
    'summary': '서버 형식 회귀 검증 자료',
    'tags': ['AI·데이터'],
    ...digest,
  },
  ...extra,
};

Notice deadlineNotice(
  String id,
  String? date, {
  String? time,
  String evidence = '검증용 신청 마감 근거',
}) => Notice(
  serverNotice(
    id: id,
    digest: {
      'deadline': date == null
          ? null
          : {'date': date, 'time': time, 'evidence': evidence},
    },
  ),
);
