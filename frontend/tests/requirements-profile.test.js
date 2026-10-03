import test from 'node:test';
import assert from 'node:assert/strict';
import { requirementItems } from '../src/features/apply-helper/requirements.js';
import { readStoredObject, profileTags, profileValue } from '../src/shared/lib/profile.js';

test('PRD의 fields와 documents를 모두 읽고 근거 없는 항목을 버린다', () => {
  const result = requirementItems({
    fields: [
      { key: 'name', required: true, evidence: '이름을 입력하세요' },
      { key: 'phone', evidence: ' ' },
      { key: 'address', evidence: '주소' },
      { key: 'other', label: '참가 동기', evidence: '참가 동기 작성' },
    ],
    documents: [
      { name: '재학증명서', condition: '재학생만', evidence: '재학증명서 제출' },
      { name: '근거 없음' },
    ],
  });
  assert.deepEqual(
    result.fields.map((item) => item.key),
    ['name', 'other'],
  );
  assert.equal(result.documents[0].condition, '재학생만');
  assert.equal(result.documents.length, 1);
  assert.deepEqual(requirementItems(null), { fields: [], documents: [] });
});

test('유효하지 않거나 차단된 저장소로 화면을 중단시키지 않는다', () => {
  for (const data of ['null', '[]', '42', '{bad']) {
    assert.deepEqual(readStoredObject({ getItem: () => data }, 'key'), {});
  }
  assert.deepEqual(
    readStoredObject(
      {
        getItem: () => {
          throw new Error('blocked');
        },
      },
      'key',
    ),
    {},
  );
  assert.deepEqual(profileTags({ tags: '개발' }), []);
  assert.deepEqual(profileTags({ tags: ['개발', '미확정 태그'] }), ['개발']);
});

test('지원용 이력 항목은 history에서 읽어 사람이 복사할 글로 만든다', () => {
  const profile = {
    history: { awards: [{ title: '테스트 수상', date: '2026-09' }], certificates: ['가상 자격증'] },
  };
  assert.equal(profileValue(profile, 'awards'), '테스트 수상 · 2026-09');
  assert.equal(profileValue(profile, 'certificates'), '가상 자격증');
  assert.equal(profileValue(profile, 'phone'), null);
  assert.equal(profileValue(profile, 'other'), null);
  assert.equal(profileValue(profile, '__proto__'), null);
});
