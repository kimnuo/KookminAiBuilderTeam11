import 'package:flutter_test/flutter_test.dart';

import 'package:kmu_notice/features/profile/pii_masker.dart';

void main() {
  test('전화번호·이메일·학번 형태를 모두 가린다', () {
    const input = '연락처 010-1234-5678, 01098765432, 02-123-4567\n'
        '메일 test.user@example.com\n'
        '학번 20231234 / 2019-03 입학';
    final r = PiiMasker.mask(input);

    expect(r.text, isNot(contains('1234-5678')));
    expect(r.text, isNot(contains('01098765432')));
    expect(r.text, isNot(contains('123-4567')));
    expect(r.text, isNot(contains('example.com')));
    expect(r.text, isNot(contains('20231234')));
    expect(r.counts, {'이메일': 1, '전화번호': 3, '학번': 1});
  });

  test('연도나 짧은 숫자는 건드리지 않는다', () {
    final r = PiiMasker.mask('2025년 해커톤 3위, 참가 120팀');
    expect(r.total, 0);
    expect(r.text, '2025년 해커톤 3위, 참가 120팀');
  });
}
