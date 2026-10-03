import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kmu_notice/features/apply_helper/requirement_field.dart';
import 'package:kmu_notice/features/apply_helper/requirements.dart';

const _field = {'key': 'email', 'required': true, 'evidence': '가상 이메일 입력 근거'};

void main() {
  _validationTests();
  _documentTest();
  _copyTests();
  _emptyValueTest();
}

void _validationTests() {
  test('근거가 없는 개인정보 항목은 숨긴다', () {
    expect(
      requirementFields({
        'fields': [
          {..._field, 'evidence': ''},
        ],
      }),
      isEmpty,
    );
  });
  test('허용한 키 밖의 개인정보 항목은 숨긴다', () {
    expect(
      requirementFields({
        'fields': [
          {..._field, 'key': 'unknown'},
        ],
      }),
      isEmpty,
    );
  });
  test('other 항목에는 원문 항목 이름이 있어야 한다', () {
    expect(
      requirementFields({
        'fields': [
          {..._field, 'key': 'other'},
        ],
      }),
      isEmpty,
    );
    expect(
      requirementFields({
        'fields': [
          {..._field, 'key': 'other', 'label': '가상 항목'},
        ],
      }),
      hasLength(1),
    );
  });
}

void _documentTest() {
  test('필요 서류에는 이름과 근거가 모두 있어야 한다', () {
    final data = {
      'documents': [
        {'name': '예시 서류', 'evidence': '가상 제출 근거'},
        {'name': ' ', 'evidence': '가상 제출 근거'},
        {'name': '근거 없는 서류', 'evidence': ''},
      ],
    };
    expect(requirementDocuments(data), hasLength(1));
  });
}

void _copyTests() {
  for (final fails in [false, true]) {
    testWidgets('복사 ${fails ? '실패 시 직접 선택 안내' : '성공 시 저장된 값만 전달'}', (
      tester,
    ) async {
      String? copied;
      final messenger =
          TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
      messenger.setMockMethodCallHandler(SystemChannels.platform, (call) async {
        if (call.method == 'Clipboard.setData') {
          if (fails) throw PlatformException(code: 'denied');
          copied = call.arguments['text'];
        }
        return null;
      });
      addTearDown(
        () => messenger.setMockMethodCallHandler(SystemChannels.platform, null),
      );
      await _pump(tester, 'review@example.com');
      await tester.tap(find.text('복사'));
      await tester.pumpAndSettle();
      expect(copied, fails ? null : 'review@example.com');
      expect(
        find.text(fails ? '복사하지 못했어요. 값을 직접 선택해 주세요.' : '지원 정보를 복사했어요.'),
        findsOneWidget,
      );
    });
  }
}

void _emptyValueTest() {
  testWidgets('빈 지원 정보의 복사 버튼은 꺼져 있다', (tester) async {
    await _pump(tester, '');
    final button = tester.widget<TextButton>(find.byType(TextButton));
    expect(button.onPressed, isNull);
    expect(find.text('내 지원 정보에 입력해 주세요.'), findsOneWidget);
  });
}

Future<void> _pump(WidgetTester tester, String value) => tester.pumpWidget(
  MaterialApp(
    home: Scaffold(
      body: RequirementField(field: _field, value: value),
    ),
  ),
);
