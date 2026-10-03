import assert from 'node:assert/strict';
import test from 'node:test';
import { matchedTags, rankByTags } from '../src/shared/lib/profile-tags.js';

const notices = [
  { id: 'a', title: '졸업앨범 촬영 예약', ai: { summary: ['졸업 예정자 안내'] } },
  { id: 'b', title: '생성형 AI 데이터 분석 강좌', ai: { summary: ['실습 중심'] } },
  { id: 'c', title: 'ICPC 참가 신청', originalTitle: '대학생 프로그래밍 경시대회', ai: {} },
];

test('태그 낱말이 제목·원 제목·요약에 있으면 겹친다고 본다', () => {
  assert.deepEqual(matchedTags(notices[1], ['AI·데이터', '개발']), ['AI·데이터']);
  assert.deepEqual(matchedTags(notices[2], ['AI·데이터', '개발']), ['개발']);
  assert.deepEqual(matchedTags(notices[0], ['AI·데이터', '개발']), []);
});

test('영문 낱말은 다른 단어 속에서 걸리지 않고, 기관명은 개발 태그에 걸리지 않는다', () => {
  const mail = { title: '채용 안내', ai: { summary: ['email 로 제출, daily 확인'] } };
  assert.deepEqual(matchedTags(mail, ['AI·데이터']), []);
  const college = { title: '소프트웨어융합대학 성적장학금', originalTitle: 'SW중심대학 장학금' };
  assert.deepEqual(matchedTags(college, ['개발']), []);
});

test('켜진 태그와 겹치는 글을 위로 올리고 나머지는 원래 순서를 지킨다', () => {
  assert.deepEqual(
    rankByTags(notices, ['AI·데이터', '개발']).map((n) => n.id),
    ['b', 'c', 'a'],
  );
  assert.equal(rankByTags(notices, []), notices);
});
