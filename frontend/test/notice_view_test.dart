import 'package:flutter_test/flutter_test.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_search.dart';

import 'support/notice_fixture.dart';

void main() {
  _searchTests();
  _applicationTests();
  _evidenceTests();
  _statusTests();
  _legacyTest();
}

void _searchTests() {
  for (final query in ['AI·데이터', 'ａｉ 데이터', 'SW사업단', '원 제목', '행사 대외활동']) {
    test('서버 필드 검색: $query', () {
      expect(matchesSearch(Notice(serverNotice()), query), true);
    });
  }
  test('digest.tags만 읽고 추천 매칭 태그를 전체 태그로 쓰지 않는다', () {
    final n = Notice(
      serverNotice(
        extra: {
          'matchedTags': ['무관한태그'],
        },
      ),
    );
    expect(n.tags, ['AI·데이터']);
    expect(matchesSearch(n, '무관한태그'), false);
  });
  test('다중 검색어는 모두 일치해야 한다', () {
    final n = Notice(serverNotice());
    expect(matchesSearch(n, 'AI 서버'), true);
    expect(matchesSearch(n, 'AI 없는단어'), false);
  });
  test('알 수 없는 태그 자료형은 빈 배열', () {
    expect(Notice(serverNotice(digest: {'tags': '태그'})).tags, isEmpty);
  });
}

void _applicationTests() {
  for (final label in ['신청 방법', '접수처', '제출 경로', '예약방법']) {
    test('근거 있는 $label 표시', () {
      final n = Notice(
        serverNotice(
          digest: {
            'keyPoints': [_point(label)],
          },
        ),
      );
      expect(n.apply, contains('온라인 접수'));
      expect(n.apply, contains('근거: 검증용 온라인 접수 근거'));
    });
  }
  test('기간과 대상만 있으면 신청 방법을 만들지 않는다', () {
    final n = Notice(
      serverNotice(
        digest: {
          'keyPoints': [_point('신청 기간')],
        },
      ),
    );
    expect(n.apply, isNull);
    expect(n.keyPoints, hasLength(1));
  });
}

void _evidenceTests() {
  test('근거 없는 신청 방법·필수 사항은 숨긴다', () {
    final n = Notice(
      serverNotice(
        digest: {
          'keyPoints': [
            {..._point('신청 방법'), 'evidence': ' '},
          ],
          'requirements': [
            {'text': '임의 서류', 'evidence': ''},
          ],
        },
      ),
    );
    expect(n.apply, isNull);
    expect(n.keyPoints, isEmpty);
    expect(n.requiredActions, isEmpty);
  });
}

Map<String, dynamic> _point(String label) => {
  'label': label,
  'value': '온라인 접수',
  'evidence': '검증용 온라인 접수 근거',
};

void _statusTests() {
  for (final status in ['pending', 'failed']) {
    test('$status는 원 제목·출처만 사용하고 AI 결과는 숨긴다', () {
      final n = Notice(
        serverNotice(
          digest: {
            'status': status,
            'keyPoints': [_point('신청 방법')],
            'requirements': [
              {'text': '가상 필수 항목', 'evidence': '가상 근거'},
            ],
          },
        ),
      );
      expect(n.title, '검증용 공고 원 제목');
      expect(n.ai, isEmpty);
      expect(n.tags, isEmpty);
      expect(n.apply, isNull);
      expect(n.keyPoints, isEmpty);
      expect(n.requiredActions, isEmpty);
    });
  }
  test('빈 요약 제목은 원 제목으로 대체', () {
    expect(Notice(serverNotice(digest: {'title': ' '})).title, '검증용 공고 원 제목');
  });
}

void _legacyTest() {
  test('기존 ai 형식도 그대로 지원', () {
    final n = Notice({
      'id': 'legacy',
      'title': '기존 공고',
      'ai': {
        'status': 'done',
        'tags': ['개발'],
        'summary': ['기존 요약'],
        'apply': '접수 링크',
      },
    });
    expect(n.title, '기존 공고');
    expect(n.tags, ['개발']);
    expect(n.apply, '접수 링크');
  });
}
