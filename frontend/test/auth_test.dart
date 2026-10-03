import 'package:flutter_test/flutter_test.dart';

import 'package:kmu_notice/features/auth/signup_rules.dart';
import 'test_helpers.dart';

void main() {
  test('비밀번호는 8자 이상, 영문과 숫자를 모두 포함해야 한다', () {
    expect(SignupRules.passwordValid('abcdefgh'), isFalse);
    expect(SignupRules.passwordValid('12345678'), isFalse);
    expect(SignupRules.passwordValid('abc123'), isFalse);
    expect(SignupRules.passwordValid('abcd1234'), isTrue);
  });

  testWidgets('규칙에 안 맞는 비밀번호면 가입 버튼이 꺼져 있다', (tester) async {
    await pumpApp(tester);
    await tapText(tester, '시작하기');

    await fillFields(tester, ['rule_user', 'onlyletters']);
    expect(ctaEnabled(tester, '가입하기'), isFalse);

    await fillFields(tester, ['rule_user', 'letters123']);
    expect(ctaEnabled(tester, '가입하기'), isTrue);
  });

  testWidgets('이미 있는 닉네임으로는 가입할 수 없다', (tester) async {
    await pumpApp(tester);
    await tapText(tester, '시작하기');
    await fillFields(tester, ['dup_user', 'testpass123']);
    await tapText(tester, '가입하기');
    expect(find.text('[필수] 개인정보 수집·이용에 동의해요'), findsOneWidget);

    await pumpApp(tester);
    await tapText(tester, '시작하기');
    await fillFields(tester, ['dup_user', 'other4567']);
    await tapText(tester, '가입하기');
    expect(find.text('이미 사용 중인 닉네임이에요.'), findsOneWidget);
  });

  testWidgets('가입한 계정으로만 로그인된다', (tester) async {
    await pumpApp(tester);
    await tapText(tester, '시작하기');
    await fillFields(tester, ['login_user', 'testpass123']);
    await tapText(tester, '가입하기');

    await pumpApp(tester);
    await tapText(tester, '이미 계정이 있어요');
    await fillFields(tester, ['login_user', 'wrongpass1']);
    await tapText(tester, '로그인');
    expect(find.text('닉네임 또는 비밀번호가 맞지 않아요.'), findsOneWidget);

    await fillFields(tester, ['login_user', 'testpass123']);
    await tapText(tester, '로그인');
    expect(find.text('피드 화면 자리 (프론트 B)'), findsOneWidget);
  });
}
