import 'package:flutter_test/flutter_test.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_media_data.dart';

import 'support/notice_fixture.dart';

void main() {
  _posterTests();
  _posterFileTests();
  _posterDedupeTests();
  _urlTests();
}

void _posterTests() {
  for (final type in ['png', 'JPEG', 'image/webp', 'gif']) {
    test('previewMedia 없이 서버 $type 첨부를 포스터로 표시', () {
      final n = Notice(
        serverNotice(
          extra: {
            'attachments': [
              {'name': '검증용 포스터', 'type': type, 'url': '/files/poster'},
            ],
          },
        ),
      );
      expect(n.posters.single['url'], 'https://example.com/files/poster');
    });
  }
}

void _posterFileTests() {
  test('다운로드 URL에 확장자가 없어도 파일명으로 판별', () {
    final n = Notice(
      serverNotice(
        extra: {
          'attachments': [
            {'name': 'poster.png', 'url': '/download?id=1', 'type': 'unknown'},
          ],
        },
      ),
    );
    expect(n.posters, hasLength(1));
  });
  test('PDF는 이미지로 해석하지 않는다', () {
    final n = Notice(
      serverNotice(
        extra: {
          'attachments': [
            {'name': 'guide.pdf', 'type': 'pdf', 'url': '/guide.pdf'},
          ],
        },
      ),
    );
    expect(n.posters, isEmpty);
    expect(n.attachments.single['url'], 'https://example.com/guide.pdf');
  });
}

void _posterDedupeTests() {
  test('중복 이미지 URL은 한 번만 미리보기', () {
    final file = {'name': 'poster.png', 'type': 'png', 'url': '/poster.png'};
    final n = Notice(
      serverNotice(
        extra: {
          'attachments': [file, file],
        },
      ),
    );
    expect(n.posters, hasLength(1));
  });
  test('기존 데모 포스터 asset 유지', () {
    final n = Notice(
      serverNotice(
        extra: {
          'previewMedia': {
            'poster': {
              'asset': 'assets/demo/media/ai-challenge-poster.png',
              'alt': '예시 포스터',
            },
          },
        },
      ),
    );
    expect(
      n.posters.single['asset'],
      'assets/demo/media/ai-challenge-poster.png',
    );
  });
}

void _urlTests() {
  for (final value in [
    '',
    'javascript:alert(1)',
    'file:///tmp/poster.png',
    'data:image/png;base64,a',
    'https://user:pass@example.com/poster.png',
  ]) {
    test('미디어 URL 거절: $value', () {
      expect(noticeMediaUrl(value, 'https://example.com/notices/1'), isNull);
    });
  }
  test('공고 경로 기준 상대 URL을 해석', () {
    expect(
      noticeMediaUrl('../poster.png', 'https://example.com/notices/1'),
      'https://example.com/poster.png',
    );
  });
  test('이미지 URL이 없는 응답은 포스터를 만들지 않는다', () {
    expect(Notice(serverNotice()).posters, isEmpty);
  });
}
