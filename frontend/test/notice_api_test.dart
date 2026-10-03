import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:kmu_notice/shared/api/api_client.dart';
import 'package:kmu_notice/shared/api/notice_api.dart';

import 'support/notice_fixture.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  tearDown(() {
    NoticeApi.client.close();
    NoticeApi.client = http.Client();
  });
  _responseTests();
  _errorTests();
}

void _responseTests() {
  test('실서버 피드 items 응답과 digest.tags 해석', () async {
    NoticeApi.client = MockClient((request) async {
      expect(request.url.path, '/api/feed');
      expect(request.url.queryParameters['sort'], 'deadline');
      return _json({
        'items': [serverNotice()],
      });
    });
    final items = await NoticeApi.feed('deadline');
    expect(items.single.tags, ['AI·데이터']);
  });
  test('실서버 상세 id를 URL 인코딩', () async {
    NoticeApi.client = MockClient((request) async {
      expect(request.url.pathSegments.last, 'test/notice');
      return _json(serverNotice(id: 'test/notice'));
    });
    expect((await NoticeApi.detail('test/notice')).id, 'test/notice');
  });
  test('준비 API 404는 원문 안내 상태로 처리', () async {
    NoticeApi.client = MockClient((_) async => http.Response('{}', 404));
    final data = await NoticeApi.requirements('review-404');
    expect(data['status'], 'unavailable');
    expect(data['fields'], isEmpty);
  });
}

void _errorTests() {
  test('연결 실패를 데모 데이터로 대체하지 않는다', () async {
    NoticeApi.client = MockClient((_) async => http.Response('{}', 500));
    await expectLater(
      NoticeApi.feed('recommend'),
      throwsA(isA<ApiException>()),
    );
  });
  test('준비 API 500은 오류로 표시하고 실패 캐시는 재시도', () async {
    var calls = 0;
    NoticeApi.client = MockClient((_) async {
      calls++;
      return calls == 1 ? http.Response('{}', 500) : _json({'fields': []});
    });
    await expectLater(
      NoticeApi.requirements('review-retry'),
      throwsA(isA<ApiException>()),
    );
    expect(await NoticeApi.requirements('review-retry'), {'fields': []});
    expect(calls, 2);
  });
}

http.Response _json(Object body) => http.Response.bytes(
  utf8.encode(jsonEncode(body)),
  200,
  headers: {'Content-Type': 'application/json; charset=utf-8'},
);
