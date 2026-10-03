import 'package:flutter_test/flutter_test.dart';

import 'test_helpers.dart';

void main() {
  testWidgets('가입 안내에서 가입과 로그인을 고를 수 있다', (tester) async {
    await pumpApp(tester);
    expect(find.text('시작하기'), findsOneWidget);
    expect(find.text('이미 계정이 있어요'), findsOneWidget);
  });
}
