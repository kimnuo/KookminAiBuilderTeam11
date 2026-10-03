import assert from 'node:assert/strict';
import test from 'node:test';
import {
  activeTags,
  matchedTags,
  otherTags,
  rankByTags,
  tagCounts,
  tagState,
  toggleTag,
  withTags,
} from '../src/shared/lib/profile-tags.js';

const notices = [
  { id: 'a', title: '졸업앨범 촬영 예약', ai: { summary: ['졸업 예정자 안내'] } },
  { id: 'b', title: '생성형 AI 데이터 분석 강좌', ai: { summary: ['실습 중심'] } },
  { id: 'c', title: 'ICPC 참가 신청', originalTitle: '대학생 프로그래밍 경시대회', ai: {} },
];

function withStorage(run) {
  const store = {};
  const previous = globalThis.localStorage;
  globalThis.localStorage = {
    getItem: (key) => store[key] ?? null,
    setItem: (key, value) => {
      store[key] = value;
    },
  };
  try {
    run();
  } finally {
    globalThis.localStorage = previous;
  }
}

test('태그 낱말이 제목·원 제목·요약에 있으면 겹친다고 본다', () => {
  assert.deepEqual(matchedTags(notices[1], ['AI·데이터', '개발']), ['AI·데이터']);
  assert.deepEqual(matchedTags(notices[2], ['AI·데이터', '개발']), ['개발']);
  assert.deepEqual(matchedTags(notices[0], ['AI·데이터', '개발']), []);
});

test('한 페이지 요약(digest) 속 주요 내역·필수 사항·기타도 같이 본다', () => {
  const notice = {
    title: '2026-2학기 프로그램 안내',
    digest: {
      keyPoints: [{ label: '교육 내용', value: '머신러닝 실습' }],
      requirements: [{ text: '포트폴리오 제출' }],
      etc: ['창업 동아리 연계'],
    },
  };
  assert.deepEqual(matchedTags(notice, ['AI·데이터', '기획·창업', '봉사']), [
    'AI·데이터',
    '기획·창업',
  ]);
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

test('정렬과 상관없이 글마다 겹친 태그를 적어 둔다', () => {
  assert.deepEqual(
    withTags(notices, ['AI·데이터']).map((n) => n.matchedTags),
    [[], ['AI·데이터'], []],
  );
  assert.deepEqual(
    withTags(notices, []).map((n) => n.matchedTags),
    [[], [], []],
  );
});

test('내 태그는 기본으로 켜지고, 내 태그가 아닌 분야 태그는 눌러야 켜진다', () => {
  withStorage(() => {
    tagState.tags = ['AI·데이터'];
    assert.deepEqual(activeTags(), ['AI·데이터']);
    assert.ok(otherTags().includes('개발'));
    assert.ok(!otherTags().includes('AI·데이터'));

    toggleTag('개발');
    assert.deepEqual(activeTags(), ['AI·데이터', '개발']);
    toggleTag('AI·데이터');
    assert.deepEqual(activeTags(), ['개발']);
    toggleTag('개발');
    assert.deepEqual(activeTags(), []);
    toggleTag('AI·데이터');
    assert.deepEqual(activeTags(), ['AI·데이터']);
    tagState.tags = [];
  });
});

test('태그마다 겹치는 글이 몇 개인지 센다', () => {
  tagState.tags = ['AI·데이터'];
  const counts = tagCounts(notices);
  assert.equal(counts['AI·데이터'], 1);
  assert.equal(counts['개발'], 1);
  assert.equal(counts['봉사'], undefined);
  tagState.tags = [];
});
