import assert from 'node:assert/strict';
import test from 'node:test';
import { rankByFit, toSituation, withFits } from '../src/shared/lib/recommend.js';

test('서버로 보내는 상황에는 이름·학번·연락처를 넣지 않는다', () => {
  const profile = {
    name: '가상 사용자',
    studentId: '20000000',
    phone: '010-0000-0000',
    email: 'student@example.com',
    major: '소프트웨어학부',
    year: 3,
    interests: ['장학', '없는분류'],
  };
  const body = toSituation(profile, ['AI·데이터']);
  assert.deepEqual(body, {
    situation: {
      major: '소프트웨어학부',
      year: 3,
      status: '재학',
      graduating: false,
      interests: ['장학'],
    },
    tags: ['AI·데이터'],
  });
  assert.ok(!JSON.stringify(body).includes('20000000'));
  assert.ok(!JSON.stringify(body).includes('010-'));
});

test('학년이 숫자가 아니면 null 로 보낸다', () => {
  assert.equal(toSituation({ year: '모름' }, []).situation.year, null);
  assert.equal(toSituation({ year: '3학년' }, []).situation.year, 3);
});

test('적합도를 못 받은 글은 fit 이 null 이고, 될 가능성 + 태그 겹침 순으로 정렬한다', () => {
  const notices = [
    { id: 'a', matchedTags: [] },
    { id: 'b', matchedTags: [] },
    { id: 'c', matchedTags: ['개발'] },
  ];
  const fits = { a: { chance: 90, reason: '자격 충족' }, c: { chance: 10, reason: '대상 아님' } };
  const merged = withFits(notices, fits);
  assert.equal(merged[1].fit, null);
  // a 90 > b 50(모름) > c 10+15
  assert.deepEqual(
    rankByFit(merged).map((item) => item.id),
    ['a', 'b', 'c'],
  );
});

test('가능성이 같으면 태그가 겹치는 글이 먼저 온다', () => {
  const same = withFits(
    [
      { id: 'a', matchedTags: [] },
      { id: 'b', matchedTags: ['개발'] },
    ],
    { a: { chance: 60, reason: '' }, b: { chance: 60, reason: '' } },
  );
  assert.deepEqual(
    rankByFit(same).map((item) => item.id),
    ['b', 'a'],
  );
});
