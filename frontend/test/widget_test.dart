import 'package:flutter_test/flutter_test.dart';

import 'package:kmu_notice/main.dart';

void main() {
  testWidgets('첫 화면에서 가입과 로그인을 고를 수 있다', (tester) async {
    await tester.pumpWidget(const KmuNoticeApp());
    await tester.pumpAndSettle();
    expect(find.text('시작하기'), findsOneWidget);
    expect(find.text('이미 계정이 있어요'), findsOneWidget);
  });
}
