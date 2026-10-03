import test from 'node:test';
import assert from 'node:assert/strict';
import { getFeed, getNotice, getRequirements } from '../src/shared/api/api-client.js';

test('API 요청에는 sort/userId/id만 넣고 지원 개인정보를 보내지 않는다', async () => {
  const calls = [];
  const previousFetch = globalThis.fetch;
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options });
    return new Response(JSON.stringify(url.includes('/feed?') ? [] : {}));
  };
  try {
    await getFeed('recommend', 'test-user', undefined);
    await getRequirements('test-only', undefined);
    assert.equal(calls[0].url, './api/feed?sort=recommend&userId=test-user');
    assert.equal(calls[1].url, './api/notices/test-only/requirements');
    assert.ok(calls.every((call) => !call.body && call.credentials === 'same-origin'));
    assert.ok(!JSON.stringify(calls).includes('phone'));
    assert.ok(!JSON.stringify(calls).includes('studentId'));
  } finally {
    globalThis.fetch = previousFetch;
  }
});

test('잘못된 API 응답과 HTTP 실패를 빈 성공 결과로 숨기지 않는다', async () => {
  const previousFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => new Response('{}');
    await assert.rejects(getFeed('deadline', null, undefined), /응답 형식/);
    await assert.rejects(getNotice('test-only', undefined), /공고 응답 형식/);
    globalThis.fetch = async () => new Response('', { status: 500 });
    await assert.rejects(getFeed('recommend', null, undefined), /500/);
  } finally {
    globalThis.fetch = previousFetch;
  }
});
