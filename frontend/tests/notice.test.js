import test from 'node:test';
import assert from 'node:assert/strict';
import { safeUrl } from '../src/shared/lib/html.js';
import { feedCard } from '../src/features/feed/FeedCard.js';
import { filterNotices } from '../src/shared/lib/notice-data.js';

const notice = {
  id: 'test-only',
  title: '검증용 공고',
  url: 'https://example.com/notice',
  source: { id: 'test-source', name: '검증용 출처' },
  ai: { status: 'done', categories: ['장학'], tags: ['개발'], summary: ['첫 줄'], deadline: null },
};
const filters = { query: '', category: '', source: '', sort: 'recommend' };

test('AI 실패·처리 중이면 남아 있는 AI 출력도 사용하지 않는다', () => {
  for (const status of ['failed', 'pending']) {
    const html = feedCard(
      { ...notice, recommendationReasons: ['추천근거'], ai: { ...notice.ai, status } },
      'recommend',
    );
    assert.ok(!html.includes('첫 줄'));
    assert.ok(!html.includes('추천근거'));
    assert.ok(!html.includes('D-'));
  }
  assert.ok(feedCard({ ...notice, ai: { status: 'failed' } }, 'recommend').includes('원문 보기'));
});

test('분야·출처·검색 필터를 함께 적용하고 추천 피드에서 지난 마감을 뺀다', () => {
  const expired = {
    ...notice,
    id: 'expired',
    ai: { ...notice.ai, deadline: { date: '2026-10-02', time: null, evidence: '10월 2일까지' } },
  };
  const items = [notice, expired];
  assert.deepEqual(
    filterNotices(
      items,
      { ...filters, query: '개발', category: '장학', source: 'test-source' },
      new Date('2026-10-03T12:00:00+09:00'),
    ).map((item) => item.id),
    ['test-only'],
  );
  assert.equal(filterNotices(items, { ...filters, category: '채용·인턴' }).length, 0);
});

test('원문 링크는 HTTP/HTTPS만 허용하고 HTML 입력을 문자로 표시한다', () => {
  for (const url of ['javascript:alert(1)', 'data:text/html,bad', 'file:///tmp/test'])
    assert.equal(safeUrl(url), null);
  const html = feedCard({ ...notice, title: '<script>bad</script>' }, 'recommend');
  assert.ok(!html.includes('<script>'));
  assert.ok(html.includes('&lt;script&gt;'));
});
