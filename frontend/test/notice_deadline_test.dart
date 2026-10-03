import 'package:flutter_test/flutter_test.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';

import 'support/notice_fixture.dart';

final _now = DateTime.parse('2026-10-03T08:00:00Z'); // 한국 시간 17:00

void main() {
  _validityTests();
  _boundaryTests();
  _sortingTests();
}

void _validityTests() {
  final cases = [
    ('2024-02-29', null, '근거', true),
    ('2026-02-29', null, '근거', false),
    ('2026-04-31', null, '근거', false),
    ('2026-13-01', null, '근거', false),
    ('2026-10-03', '23:59', '근거', true),
    ('2026-10-03', '24:00', '근거', false),
    ('2026-10-03', '9:00', '근거', false),
    ('2026-10-03', null, ' ', false),
    ('2026-1-3', null, '근거', false),
  ];
  for (final (date, time, evidence, valid) in cases) {
    test('마감 검증 $date $time [$evidence]', () {
      final n = deadlineNotice('valid', date, time: time, evidence: evidence);
      expect(validDeadline(n) != null, valid);
    });
  }
}

void _boundaryTests() {
  final cases = [
    ('2026-10-02', null, true, '마감'),
    ('2026-10-03', null, false, '오늘 마감'),
    ('2026-10-03', '16:59', true, '마감'),
    ('2026-10-03', '17:00', true, '마감'),
    ('2026-10-03', '17:01', false, '오늘 마감'),
    ('2026-10-04', null, false, 'D-1'),
    (null, null, false, '원문 확인'),
  ];
  for (final (date, time, expired, label) in cases) {
    test('한국 시간 마감 경계 $date $time', () {
      final n = deadlineNotice('boundary', date, time: time);
      expect(deadlineExpired(n, now: _now), expired);
      expect(deadlineLabel(n, now: _now), label);
    });
  }
  test('UTC 15시는 한국 시간 다음 날 0시', () {
    final midnight = DateTime.parse('2026-10-03T15:00:00Z');
    expect(koreaToday(midnight), DateTime.utc(2026, 10, 4));
    expect(
      deadlineExpired(deadlineNotice('kst', '2026-10-03'), now: midnight),
      true,
    );
  });
}

void _sortingTests() {
  test('진행 중 → 마감 미확인 → 마감됨 순서', () {
    final list = [
      deadlineNotice('expired', '2026-10-02'),
      deadlineNotice('later', '2026-10-05'),
      deadlineNotice('unknown', null),
      deadlineNotice('soon', '2026-10-03', time: '17:01'),
    ];
    list.sort((a, b) => compareDeadline(a, b, now: _now));
    expect(list.map((n) => n.id), ['soon', 'later', 'unknown', 'expired']);
  });
  test('같은 마감과 게시일은 id로 일정하게 정렬', () {
    final a = deadlineNotice('a', '2026-10-04');
    final b = deadlineNotice('b', '2026-10-04');
    expect(compareDeadline(a, b, now: _now), lessThan(0));
    expect(compareDeadline(b, a, now: _now), greaterThan(0));
    expect(compareDeadline(a, a, now: _now), 0);
  });
  test('근거 없는 과거 날짜는 마감 미확인으로 취급', () {
    final invalid = deadlineNotice('unknown', '2026-10-01', evidence: '');
    final expired = deadlineNotice('expired', '2026-10-02');
    expect(compareDeadline(invalid, expired, now: _now), lessThan(0));
    expect(deadlineLabel(invalid, now: _now), '원문 확인');
  });
}
