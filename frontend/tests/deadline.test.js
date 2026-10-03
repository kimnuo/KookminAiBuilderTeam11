import test from 'node:test';
import assert from 'node:assert/strict';
import { validDeadline, deadlineExpired, deadlineLabel } from '../src/shared/lib/deadline.js';

const now = new Date('2026-10-03T14:00:00+09:00');
const deadline = (date = '2026-10-03', time = '17:00') => ({
  date,
  time,
  evidence: '마감 10월 3일 17시',
});

test('마감일에는 원문 근거와 올바른 날짜·시각이 필요하다', () => {
  for (const value of [
    null,
    { date: '2026-10-03' },
    { ...deadline(), evidence: ' ' },
    deadline('2026-02-30'),
    deadline('2026-10-03', '24:00'),
  ]) {
    assert.equal(validDeadline(value), null);
    assert.equal(deadlineLabel(value, now).label, '원문 확인');
  }
});

test('당일 남은 마감과 이미 지난 마감을 구분한다', () => {
  assert.equal(deadlineLabel(deadline(), now).label, '오늘 마감');
  assert.equal(deadlineLabel(deadline('2026-10-03', '13:59'), now).label, '마감');
  assert.equal(deadlineExpired(deadline('2026-10-03', '14:00'), now), true);
});

test('D-day는 경과 시간 대신 한국 날짜를 기준으로 계산한다', () => {
  const late = new Date('2026-10-03T23:55:00+09:00');
  assert.equal(deadlineLabel(deadline('2026-10-04', '00:05'), late).label, 'D-1');
  assert.equal(deadlineLabel(deadline('2026-10-10', '00:05'), late).label, 'D-7');
});

test('알 수 없는 마감 시각을 만들지 않는다', () => {
  const value = deadline('2026-10-03', null);
  assert.equal(validDeadline(value).time, null);
  assert.equal(deadlineExpired(value, new Date('2026-10-03T23:59:59+09:00')), false);
  assert.equal(deadlineExpired(value, new Date('2026-10-04T00:00:00+09:00')), true);
});
