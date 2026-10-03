import 'package:flutter_test/flutter_test.dart';
import 'package:kmu_notice/features/feed/feed_controller.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';

import 'support/notice_fixture.dart';

void main() {
  _filterTests();
  _selectionTests();
}

void _filterTests() {
  test('추천 순은 이미 마감된 글을 제외', () {
    final c = _controller();
    expect(c.visible.map((n) => n.id), ['open', 'unknown']);
  });
  test('마감 임박 순은 지난 글을 맨 뒤에 표시', () {
    final c = _controller()..sort = 'deadline';
    expect(c.visible.map((n) => n.id), ['open', 'unknown', 'expired']);
  });
  test('digest.tags로 피드를 검색', () {
    final c = _controller()..query = 'AI 데이터';
    expect(c.visible, hasLength(2));
  });
  test('출처 id로 필터링', () {
    final c = _controller()..source = 'missing-source';
    expect(c.visible, isEmpty);
  });
  test('결과가 없어도 원본 피드를 바꾸지 않는다', () {
    final c = _controller()..query = '없는단어';
    expect(c.visible, isEmpty);
    expect(c.notices, hasLength(3));
  });
}

void _selectionTests() {
  test('여러 분류에 걸친 공고를 한 번만 표시', () {
    final c = _controller()
      ..notices = [
        Notice(
          serverNotice(
            extra: {
              'categories': ['장학', '취업'],
            },
          ),
        ),
      ];
    c.toggle('scholarship');
    c.toggle('career');
    expect(c.chosen, hasLength(1));
  });
  test('미선택 분류는 선택 목록에서 제외', () {
    final c = _controller();
    c.toggle('scholarship');
    expect(c.chosen, isEmpty);
    c.clearSelection();
    expect(c.chosen, hasLength(2));
  });
  test('홈 버튼은 검색·출처·카테고리 선택을 초기화', () {
    final c = _controller()
      ..query = '태그'
      ..source = 'source';
    c.toggle('activity');
    c.resetHome();
    expect(c.query, '');
    expect(c.source, '');
    expect(c.sort, 'recommend');
    expect(c.selected, isEmpty);
    expect(c.visible, hasLength(2));
  });
}

FeedController _controller() {
  final today = koreaToday();
  String date(int offset) =>
      today.add(Duration(days: offset)).toIso8601String().substring(0, 10);
  final c = FeedController()
    ..notices = [
      deadlineNotice('expired', date(-1)),
      deadlineNotice('open', date(1)),
      deadlineNotice('unknown', null),
    ];
  addTearDown(c.dispose);
  return c;
}
