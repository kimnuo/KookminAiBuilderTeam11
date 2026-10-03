/**
 * 백엔드 공지 형식(digest: 한 페이지 요약)을 화면이 쓰는 ai 형식으로 맞춘다.
 * 더미 미리보기 자료(PRD v0.4 형식, digest 없음)는 그대로 둔다.
 * 원본 digest 는 상세 화면의 주요 내역·필수 사항·기타·첨부에 그대로 쓴다.
 */
export function toView(notice) {
  if (!notice || typeof notice !== 'object' || !notice.digest) return notice;
  const digest = notice.digest;
  return {
    ...notice,
    title: digest.title || notice.originalTitle,
    ai: {
      status: digest.status,
      categories: Array.isArray(notice.categories) ? notice.categories : [],
      tags: [],
      summary: typeof digest.summary === 'string' && digest.summary ? [digest.summary] : [],
      deadline: digest.deadline ?? null,
      audience: digest.audience ?? null,
      apply: null,
    },
  };
}
