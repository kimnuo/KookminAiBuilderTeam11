import assert from 'node:assert/strict';
import test from 'node:test';
import { toView } from '../src/shared/lib/digest-view.js';

const backendNotice = {
  id: 'cs-notice-1',
  originalTitle: '원 제목',
  categories: ['졸업'],
  digest: {
    status: 'done',
    title: '요약 제목',
    summary: '요약 문장',
    deadline: { date: '2026-10-11', time: '14:00', evidence: '10월 11일 14:00' },
    audience: null,
  },
};

test('백엔드 digest 를 화면용 ai 형식으로 바꾸고 원본 digest 는 남긴다', () => {
  const view = toView(backendNotice);
  assert.equal(view.title, '요약 제목');
  assert.deepEqual(view.ai.categories, ['졸업']);
  assert.deepEqual(view.ai.summary, ['요약 문장']);
  assert.equal(view.ai.deadline.date, '2026-10-11');
  assert.equal(view.digest, backendNotice.digest);
});

test('요약 실패면 원 제목을 쓰고, digest 없는 더미 자료는 그대로 둔다', () => {
  const failed = toView({ ...backendNotice, digest: { status: 'failed', title: null } });
  assert.equal(failed.title, '원 제목');
  assert.deepEqual(failed.ai.summary, []);
  const demo = { id: 'demo', title: '더미', ai: { status: 'done' } };
  assert.equal(toView(demo), demo);
});
