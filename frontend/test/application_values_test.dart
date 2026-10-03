import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:kmu_notice/shared/lib/applicant_store.dart';
import 'package:kmu_notice/shared/lib/application_values.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => SharedPreferences.setMockInitialValues({}));
  _storageTests();
  _historyTests();
}

void _storageTests() {
  test('실서버 모드 빈 저장소에 가상 개인정보를 채우지 않는다', () async {
    final values = await applicationValues();
    expect(values['name'], '');
    expect(values['email'], '');
    expect(values['school'], '국민대학교');
  });
  test('지원 정보 저장 후 패널에서 새 값을 읽는다', () async {
    await ApplicantStore.save(ApplicantInfo({'email': 'before@example.com'}));
    expect((await applicationValues())['email'], 'before@example.com');
    await ApplicantStore.save(ApplicantInfo({'email': 'after@example.com'}));
    expect((await applicationValues())['email'], 'after@example.com');
  });
  test('비운 지원 정보는 이전 값이나 가상 값으로 대체하지 않는다', () async {
    await ApplicantStore.save(ApplicantInfo({'email': 'before@example.com'}));
    await ApplicantStore.save(ApplicantInfo({'email': null}));
    expect((await applicationValues())['email'], '');
  });
}

void _historyTests() {
  test('기기에 저장한 수상·활동을 복사용 텍스트로 변환', () async {
    SharedPreferences.setMockInitialValues({
      'profile.history': jsonEncode({
        'awards': [
          {'title': '가상 수상', 'period': '2026'},
        ],
        'activities': [
          {'name': '가상 활동', 'detail': '검증 자료'},
        ],
      }),
    });
    final values = await applicationValues();
    expect(values['awards'], '가상 수상 · 2026');
    expect(values['activities'], '가상 활동 · 검증 자료');
  });
}
