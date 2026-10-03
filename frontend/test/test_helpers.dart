import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:kmu_notice/shared/api/notice_api.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:kmu_notice/app/router.dart';
import 'package:kmu_notice/main.dart';
import 'package:kmu_notice/shared/lib/routes.dart';

Future<void> pumpApp(WidgetTester tester) async {
  SharedPreferences.setMockInitialValues({});
  NoticeApi.client = MockClient((_) async => http.Response('[]', 200));
  addTearDown(() {
    NoticeApi.client.close();
    NoticeApi.client = http.Client();
  });
  tester.view.physicalSize = const Size(1080, 2400);
  tester.view.devicePixelRatio = 3;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(const KmuNoticeApp());
  appRouter.go(Routes.welcome);
  await tester.pumpAndSettle();
}

Future<void> tapText(WidgetTester tester, String text) async {
  if (find.text(text).evaluate().isEmpty) {
    await tester.scrollUntilVisible(
      find.text(text),
      200,
      scrollable: find.byType(Scrollable).first,
    );
  }
  await tester.ensureVisible(find.text(text));
  await tester.pumpAndSettle();
  await tester.tap(find.text(text));
  await tester.pumpAndSettle();
}

Future<void> fillFields(WidgetTester tester, List<String> values) async {
  for (var i = 0; i < values.length; i++) {
    await tester.enterText(find.byType(TextField).at(i), values[i]);
  }
  await tester.pumpAndSettle();
}

bool ctaEnabled(WidgetTester tester, String label) {
  final button = tester.widget<FilledButton>(
    find.ancestor(of: find.text(label), matching: find.byType(FilledButton)),
  );
  return button.onPressed != null;
}
