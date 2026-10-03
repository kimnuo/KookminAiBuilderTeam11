# 동의 화면 문구

> **법률 검토 전 초안이다.** 개인정보 보호법 조문은 검색 요약으로만 봤고, law.go.kr 원문은 열지 않았다. 실제 서비스에 그대로 쓰기 전에 원문 대조와 검토를 받는다.

| 항목 | 내용 |
|---|---|
| 상태 | 초안 (2026-10-03, K-Builder 현장) |
| 기준 문서 | `docs/PRD.md` v0.4의 6-1절(설계 원칙, 다루는 정보와 처리 위치, 필수·선택 동의 표, 우선순위)과 16절 |
| 쓰는 곳 | `frontend/src/features/auth/`(가입, 동의, 탈퇴), `profile/`(내 이력, 내 지원 정보, PDF 올리기), `onboarding/`(자연어 입력칸) |
| 문구 버전 | `2026-10-03`. 사용자 객체의 동의 기록 필드(PRD 10절 `consent.required.version`)에 이 값을 넣는다. 문구를 고치면 날짜를 바꾼다 |
| 담당 | 문구는 현찬(PRD 12절 제안), 화면은 택준 |

## 0. 읽는 법

- **문구** 칸은 화면에 그대로 붙인다. 따옴표는 붙이지 않는다.
- `{aiServiceName}`처럼 중괄호로 감싼 곳은 프론트가 값으로 바꾼다. 아직 정하지 않은 값이다(9절).
- **비고**에 **[결정]**이 붙은 줄은 팀이 정한 뒤에 쓴다.
- 화면 문구는 합니다체, 이 문서의 설명은 ~다체로 쓴다.
- 표가 원본이다. 11절 JSON은 표에서 뽑은 복사용 사본이다. 표를 고치면 JSON도 다시 뽑는다.

## 1. 법 관련해서 확인한 수준

PRD 6-1절에 적힌 것만 옮긴다. 이 문서는 새 법적 판단을 더하지 않는다.

- 동의를 받을 때 목적, 항목, 보유·이용 기간, 거부 권리와 불이익을 알리라는 내용(개인정보 보호법 제15조 제2항)은 검색 요약으로만 봤다. 법령 원문은 열지 않았다. PRD는 발표 전에 law.go.kr에서 확인한다고 적었다.
- 주민등록번호를 받지 않는 근거(제24조의2)도 검색 요약으로만 봤다.
- PDF 분석 때 외부 AI 서비스로 글을 보낸다. 처리 위탁이나 국외 이전 고지가 필요한지는 PRD에서도 「확인 필요」로 남아 있다.
- 지원 정보(이름, 연락처 등)를 필수 동의에서 뺀 판단은 「서버가 그 정보를 모으지 않는다」는 설계에 기댄다. 이 판단이 법적으로 맞는지는 검토받지 않았다.
- 그래서 화면 문구에는 조문 번호를 넣지 않았다.

## 2. 가입 화면 안내

| 키 | 문구 | 비고 |
|---|---|---|
| `signup.nickname.label` | 닉네임 | |
| `signup.nickname.help` | 닉네임에는 실명을 쓰지 말아 주십시오. 학번, 연락처처럼 본인을 알아볼 수 있는 정보도 넣지 말아 주십시오. | 입력칸 바로 아래. PRD 6-1 표의 「가입 화면에 실명을 쓰지 말라고 안내한다」 |
| `signup.password.label` | 비밀번호 | |
| `signup.password.help` | 비밀번호는 원래 글자로 되돌릴 수 없는 방식으로 바꿔 저장합니다. | PRD의 「암호화 저장」을 실제 방식(비밀번호 전용 해시)에 맞게 풀었다 |
| `signup.password.noRecovery` | 비밀번호 찾기 기능이 없습니다. 비밀번호를 잊으면 계정을 되찾을 수 없습니다. | PRD 6절. 이메일 인증과 비밀번호 찾기는 오늘 만들지 않는다 |

## 3. 필수 동의 (가입 직후)

### 3-1. PRD의 네 가지와 맞춰 보기

| 알릴 것 (PRD 6-1) | 화면 키 |
|---|---|
| 수집·이용 목적 | `consent.required.purpose.label`, `consent.required.purpose.body` |
| 수집 항목 | `consent.required.items.label`, `consent.required.items.body` |
| 보유·이용 기간 | `consent.required.retention.label`, `consent.required.retention.body` |
| 거부 권리와 불이익 | `consent.required.refuse.label`, `consent.required.refuse.body` |

PRD 초안에서 바꾼 곳은 세 군데다.

- 수집 항목에 「관심 키워드」를 더했다. PRD 10절 구독 모델에는 직접 입력한 키워드(`keywords`)가 있는데, 6-1절 항목 표에는 없어서다. 고른 출처(`sources`)는 「관심 분야」에 들어간다고 보고 따로 적지 않았다. 둘 다 **[결정]**.
- 「비밀번호(암호화 저장)」를 「되돌릴 수 없는 방식으로 바꿔 저장」으로 풀었다. 실제로는 비밀번호 전용 해시를 쓴다(PRD 6-1 표).
- 「알림 등록 정보」가 무엇인지 괄호로 풀었다. 알림 채널이 아직 정해지지 않아서(PRD 16절) 채널 이름은 넣지 않았다.

### 3-2. 화면 문구

| 키 | 문구 | 비고 |
|---|---|---|
| `consent.required.title` | 개인정보 수집·이용 동의 (필수) | |
| `consent.required.intro` | 맞춤 공지 추천과 알림을 드리려면 아래 정보가 필요합니다. 읽어 보신 뒤 동의 여부를 골라 주십시오. | |
| `consent.required.purpose.label` | 수집·이용 목적 | |
| `consent.required.purpose.body` | 관심 분야와 이력 태그에 맞춘 공지 추천과 알림 | PRD 6-1 문구 그대로 |
| `consent.required.items.label` | 수집 항목 | |
| `consent.required.items.body` | 닉네임, 비밀번호(되돌릴 수 없는 방식으로 바꿔 저장), 학과, 학년, 관심 분야, 관심 키워드, 추천 태그, 알림 등록 정보(알림을 받을 곳을 가리키는 값) | 「관심 키워드」는 [결정] |
| `consent.required.retention.label` | 보유·이용 기간 | |
| `consent.required.retention.body` | 탈퇴할 때까지 보관합니다. 탈퇴하면 바로 삭제합니다. | PRD 6-1 문장을 합니다체로 옮겼다 |
| `consent.required.refuse.label` | 동의를 거부할 권리와 불이익 | |
| `consent.required.refuse.body` | 동의를 거부할 수 있습니다. 동의하지 않아도 공지 목록은 볼 수 있습니다. 맞춤 추천과 알림은 받을 수 없습니다. | 로그인 없이 보는 공지 목록이 있어야 참이다(10절) |
| `consent.required.excluded` | 이름, 연락처, 학번 같은 지원용 정보는 이 동의의 수집 항목이 아닙니다. 이 서비스의 서버는 그 정보를 받지 않습니다. | 항목 목록 아래에 작게. PRD 6-1: 지원 정보는 서버가 모으지 않으므로 필수 동의에 넣지 않는다 |
| `consent.required.checkbox` | [필수] 위 내용을 읽었고, 개인정보 수집·이용에 동의합니다. | 체크해야 동의 버튼이 켜진다 |
| `consent.required.agree` | 동의하고 계속 | |
| `consent.required.decline` | 동의하지 않음 | |

### 3-3. 동의하지 않을 때

`consent.required.decline`을 누르면 확인 창을 띄운다. 계정 문장은 8절에서 고른 안에 따라 하나만 쓴다.

| 키 | 문구 | 비고 |
|---|---|---|
| `consent.required.declineDialog.title` | 동의하지 않고 넘어가시겠습니까? | |
| `consent.required.declineDialog.body` | 공지 목록은 계속 볼 수 있습니다. 맞춤 추천과 알림은 받을 수 없습니다. | |
| `consent.required.declineDialog.noAccount` | 계정은 만들어지지 않습니다. 나중에 다시 가입할 수 있습니다. | [결정] 8절 A안, C안일 때만 |
| `consent.required.declineDialog.accountDeleted` | 방금 만든 계정은 바로 삭제됩니다. 나중에 다시 가입할 수 있습니다. | [결정] 8절 B안일 때만 |
| `consent.required.declineDialog.confirm` | 동의하지 않고 공지 목록 보기 | |
| `consent.required.declineDialog.cancel` | 돌아가기 | |

## 4. 선택 동의 (포트폴리오 PDF를 올릴 때)

### 4-1. PRD의 네 가지와 맞춰 보기

| 알릴 것 (PRD 6-1) | 화면 키 |
|---|---|
| 수집·이용 목적 | `consent.optional.purpose.label`, `consent.optional.purpose.body` |
| 수집 항목 | `consent.optional.items.label`, `consent.optional.items.body` |
| 보유·이용 기간 | `consent.optional.retention.label`, `consent.optional.retention.body` |
| 거부 권리와 불이익 | `consent.optional.refuse.label`, `consent.optional.refuse.body` |
| 추가 고지 (외부 AI 서비스) | `consent.optional.externalAi.label`, `consent.optional.externalAi.body` |

보유 기간 문장은 「이 서비스의 서버」로 주어를 좁혔다. 외부 AI 서비스가 받은 글을 얼마나 보관하는지는 아직 모른다. 그 서비스의 정책을 확인하기 전에는 「어디에도 저장하지 않는다」고 쓰지 않는다.

### 4-2. 화면 문구

| 키 | 문구 | 비고 |
|---|---|---|
| `consent.optional.title` | 포트폴리오 분석 동의 (선택) | |
| `consent.optional.intro` | 포트폴리오 PDF를 올리면 AI가 활동, 수상, 기술을 뽑아 내 이력 칸을 채웁니다. 이 기능을 쓸 때만 동의를 받습니다. | |
| `consent.optional.purpose.label` | 수집·이용 목적 | |
| `consent.optional.purpose.body` | 포트폴리오에서 활동, 수상, 기술을 뽑아 내 이력 칸 채우기 | PRD 6-1과 같은 뜻 |
| `consent.optional.items.label` | 수집 항목 | |
| `consent.optional.items.body` | 올린 PDF에서 뽑은 글. 전화번호, 이메일, 학번 형태의 글자는 보내기 전에 이 기기에서 가립니다. | |
| `consent.optional.retention.label` | 보유·이용 기간 | |
| `consent.optional.retention.body` | 이 서비스의 서버는 PDF 원본과 보낸 글을 저장하지 않습니다. 분석이 끝나면 버립니다. 분석 결과(활동, 수상, 기술)는 확인을 거쳐 이 기기에만 저장합니다. 확인을 거친 추천 태그만 서버에 저장합니다. | 마지막 문장은 PRD 6-1 선택 동의 표에 없다. 그 표는 「결과는 이 기기에만 저장한다」고 적었지만, 같은 절 원칙 3·4는 추천 태그를 서버에 둔다. 둘을 맞추려고 더했다 |
| `consent.optional.retention.provider` | (비워 둔다) | [결정] 외부 AI 서비스의 보관 정책을 확인한 뒤 채운다. 11절 JSON에는 넣지 않았다 |
| `consent.optional.refuse.label` | 동의를 거부할 권리와 불이익 | |
| `consent.optional.refuse.body` | 동의를 거부할 수 있습니다. 거부하면 PDF 분석 없이 이력을 직접 입력합니다. 다른 기능은 그대로 쓸 수 있습니다. | |
| `consent.optional.externalAi.label` | 외부 AI 서비스 이용 | |
| `consent.optional.externalAi.body` | 분석을 위해, 가린 글을 외부 AI 서비스({aiServiceName})로 보냅니다. | PRD 6-1 「추가 고지」. 위탁·국외 이전 고지가 필요한지는 확인 필요 |
| `consent.optional.checkbox` | [선택] 위 내용을 읽었고, 포트폴리오 분석에 동의합니다. | |
| `consent.optional.agree` | 동의하고 PDF 올리기 | |
| `consent.optional.decline` | 동의하지 않고 직접 입력하기 | 누르면 내 이력 수기 입력 화면으로 |

### 4-3. 올리기 전과 분석 뒤 안내

| 키 | 문구 | 비고 |
|---|---|---|
| `consent.optional.warn.name` | 이름과 생년월일은 자동으로 가려지지 않습니다. 올리기 전에 PDF에서 지우거나, 지운 사본을 올려 주십시오. | 동의 화면 안, 체크박스 위. PRD 6-1 표와 15절 |
| `consent.optional.warn.maskLimit` | 자동 가리기는 전화번호, 이메일, 학번 형태의 글자만 찾습니다. 다른 형태로 적힌 개인정보는 가려지지 않을 수 있습니다. | `consent.optional.warn.name` 바로 아래 |
| `consent.optional.warn.scan` | 스캔한 이미지로 된 PDF는 글자를 뽑을 수 없습니다. 이때는 이력을 직접 입력해 주십시오. | 글자 추출 결과가 비었을 때 |
| `consent.optional.review` | 분석 결과는 바로 저장되지 않습니다. 내용을 확인하고 고친 뒤 저장해 주십시오. | 검토 화면 맨 위 |

## 5. 「내 지원 정보」 화면 안내

| 키 | 문구 | 비고 |
|---|---|---|
| `applyInfo.title` | 내 지원 정보 | |
| `applyInfo.notice.local` | 이 정보는 이 기기(브라우저)에만 저장되고, 서버로 보내지 않습니다. | 화면 맨 위, 입력칸보다 먼저. PRD 6-1 문장을 합니다체로 옮겼다 |
| `applyInfo.notice.noAi` | AI 서비스로도 보내지 않습니다. 지원 준비 화면에서 내 값을 채우는 일은 이 기기 안에서 합니다. | 지원 준비(P3)가 없으면 두 번째 문장은 뺀다 |
| `applyInfo.notice.loss` | 기기를 바꾸거나 브라우저 데이터를 지우면 이 정보도 사라집니다. 다른 기기로 옮기는 기능은 없습니다. | PRD 15절 「MVP 한계로 밝힌다」 |
| `applyInfo.notice.sharedDevice` | 여러 사람이 함께 쓰는 기기에서는 입력하지 말아 주십시오. | 브라우저에 남은 값을 그 기기의 다음 사람이 볼 수 있어서다 |
| `applyInfo.notice.notCollected` | 주민등록번호와 주소는 받지 않습니다. | PRD 6-1 원칙 5 |
| `applyInfo.notice.copyOnly` | 복사 버튼은 값을 복사만 합니다. 다른 사이트의 지원서에 자동으로 입력하거나 대신 제출하지 않습니다. | P3 화면에만. PRD 6-1 원칙 6 |

## 6. 탈퇴 안내

| 키 | 문구 | 비고 |
|---|---|---|
| `withdraw.title` | 탈퇴 | |
| `withdraw.body.server` | 탈퇴하면 서버에 있는 내 정보를 바로 삭제합니다. 닉네임, 비밀번호 정보, 학과, 학년, 관심 분야, 관심 키워드, 추천 태그, 알림 등록 정보, 동의 기록이 대상입니다. | 「관심 키워드」, 「동의 기록」은 [결정] |
| `withdraw.body.irreversible` | 삭제한 정보는 되돌릴 수 없습니다. | |
| `withdraw.body.device` | 이 기기에 저장한 내 지원 정보와 내 이력은 서버에 없어서, 탈퇴만으로는 지워지지 않습니다. | 서버 삭제(`DELETE /api/me`)는 기기 저장소에 닿지 않는다 |
| `withdraw.deviceCheckbox` | 이 기기에 저장한 내 지원 정보와 내 이력도 함께 지우기 | [결정] 체크박스를 만들 때만 |
| `withdraw.confirm` | 탈퇴하기 | |
| `withdraw.cancel` | 취소 | |
| `withdraw.done.message` | 탈퇴했습니다. 서버에 있던 내 정보를 삭제했습니다. | |
| `withdraw.done.deviceKept` | 이 기기에 저장한 정보는 남아 있습니다. 지우려면 브라우저에서 이 사이트의 데이터를 삭제해 주십시오. | 기기 정보를 지우지 않았을 때만 |

## 7. 자연어 입력칸 안내

PRD 6-1 「다루는 정보와 처리 위치」 표의 「학과, 학년, 관심 분야」 줄은, AI로 보내는지 묻는 칸에 「자연어 구독 해석 때만」이라고 적었다. 그런데 필수 동의 초안에는 이 내용이 없다. 입력칸 아래에 둘 문구를 만들어 뒀다.

| 키 | 문구 | 비고 |
|---|---|---|
| `onboarding.nlInput.notice` | 이 칸에 쓴 문장은 구독 조건으로 바꾸기 위해 외부 AI 서비스({aiServiceName})로 보냅니다. 이름, 연락처, 학번은 쓰지 말아 주십시오. | [결정] 필수 동의에 넣을지, 입력칸 안내로 둘지 |

## 8. 동의 순서와 거부 시 계정 처리 (팀이 정한다)

PRD 16절의 미결 항목이다. 이 문서는 정하지 않고 선택지만 적는다.

| 안 | 순서 | 동의하지 않으면 | 장점 | 단점 | 쓰는 키 |
|---|---|---|---|---|---|
| A | 동의 화면 → 닉네임·비밀번호 입력 → 가입 | 계정을 만들지 않고 공지 목록으로 간다 | 동의 전에는 서버가 아무것도 받지 않는다. 지울 계정이 없어 삭제 처리가 필요 없다 | 화면이 하나 는다. 동의 기록을 계정에 붙이려면 가입 요청에 동의 버전을 같이 보내거나(PRD 10절 `/api/auth/signup` 계약 변경), 가입 직후 `/api/consent`를 바로 불러야 한다 | `consent.required.declineDialog.noAccount` |
| B (PRD 지금 안) | 닉네임·비밀번호 입력 → 가입 → 동의 화면 | 방금 만든 계정을 바로 지운다 | PRD 5절 흐름과 10절 API를 그대로 쓴다 | 동의 전에 닉네임과 비밀번호 해시가 서버에 저장된다. 거부 때 삭제를 따로 붙여야 한다. 동의 화면에서 창을 닫으면 동의 없는 계정이 남아서 정리 규칙이 필요하다 | `consent.required.declineDialog.accountDeleted` |
| C | 한 화면에 닉네임·비밀번호 입력칸과 동의 문구를 같이 둔다. 체크해야 가입 버튼이 켜진다 | 가입 버튼이 꺼진 채로 남고, 공지 목록으로 갈 수 있다 | 화면 수가 가장 적다. 체크 전에는 서버로 아무것도 가지 않는다 | 모바일에서 화면이 길어진다. 동의 문구가 입력칸 사이에 묻혀 덜 읽힌다. API는 A안과 같은 변경이 필요하다 | `consent.required.declineDialog.noAccount` |

B안에서 거부한 계정을 지우지 않고 남기는 변형도 있다. 이 경우 필수 동의 항목인 닉네임과 비밀번호를 동의 없이 들고 있게 되어, 이 문서의 항목 표와 맞지 않는다. 그래서 표에 넣지 않았다.

## 9. 팀이 정할 것

1. 동의 순서와 거부 시 계정 처리 (8절 A, B, C).
2. 외부 AI 서비스 이름. `{aiServiceName}`에 들어간다. PRD 16절의 「LLM API 키를 누구 것으로 쓸지」와 같이 정해진다.
3. 외부 AI 서비스가 받은 글을 보관하는지. 확인한 뒤 `consent.optional.retention.provider`를 채운다.
4. 처리 위탁이나 국외 이전 고지가 필요한지 (PRD 6-1 「확인 필요」). 법률 검토 때 묻는다.
5. 자연어 입력이 외부 AI로 간다는 고지를 어디에 둘지 (7절).
6. 수집 항목에 「관심 키워드」를 더할지, 「고른 출처」를 따로 적을지 (3-1).
7. 탈퇴 때 동의 기록까지 지울지. PRD 14절 탈퇴 검사는 「서버 데이터 0건」을 기준으로 삼는다. 동의 기록을 남겨야 하는지는 법률 검토 때 묻는다.
8. 선택 동의를 한 번 받고 계속 쓸지, PDF를 올릴 때마다 물을지. PRD 10절 사용자 객체는 `portfolioAnalysis`를 한 번 기록하는 구조다.
9. 탈퇴 화면에 「이 기기 정보도 함께 지우기」 체크박스를 만들지 (6절).
10. 로그인 없이 보는 공지 목록 화면을 만들지. 거부 문구의 「공지 목록은 볼 수 있습니다」가 참이려면 필요하다. PRD 5절 흐름은 가입부터 시작한다.
11. PDF 분석이 제안한 추천 태그를 서버에 올리는지. PRD 6-1 안에서 선택 동의 표(「결과는 이 기기에만」)와 원칙 3·4(태그는 서버)가 어긋난다. 이 문서는 원칙 쪽에 맞춰 `consent.optional.retention.body`에 태그 문장을 더했다. 팀이 다르게 정하면 그 문장을 고친다.

## 10. 화면에 붙이기 전에 확인할 것

화면 문구는 코드가 지킬 때만 참이다. 아래는 문구와, 그 문구를 참으로 만드는 확인 방법이다.

| 문구 키 | 참이 되는 조건 | 확인 방법 |
|---|---|---|
| `applyInfo.notice.local` | 내 지원 정보 값이 어떤 요청 본문에도 없다 | 브라우저 개발자 도구 네트워크 탭을 켜고 입력, 저장, 지원 준비 화면을 차례로 써 본다. 요청 본문에 그 값이 0건이어야 한다. PRD 14절 개인정보 검사(DB 0건)는 저장만 보므로 이것과 따로 한다 |
| `applyInfo.notice.noAi` | AI 호출 코드에 프로필 값이 없다 | PRD 11절대로 머지 전에 AI 호출 코드를 읽는다 |
| `consent.required.retention.body`, `withdraw.body.server` | 탈퇴하면 그 사용자의 서버 데이터가 0건이다 | PRD 14절 탈퇴 검사 |
| `signup.password.help` | DB에 비밀번호 해시만 있다 | PRD 14절 비밀번호 검사 |
| `consent.optional.items.body` | 분석 요청 본문에 전화번호·이메일·학번 형태가 0건이다 | PRD 14절 가리기 검사 |
| `consent.optional.retention.body` | `/api/profile/analyze`가 본문을 DB, 파일, 로그에 남기지 않는다 | 가상 PDF로 한 번 요청한 뒤, 그 PDF에만 있는 문장으로 서버 로그와 DB를 검색해 0건인지 본다 |
| `consent.required.refuse.body` | 로그인 없이 공지 목록을 볼 수 있다 | 동의를 거부한 뒤 공지 목록이 열리는지 눌러 본다 |

## 11. 복사용 JSON

2~7절 표에서 스크립트로 뽑았다. `consent.optional.retention.provider`는 아직 문구가 없어서 뺐다. 키는 평평한 문자열이다. i18n 라이브러리가 점을 계층으로 읽어도 겹치지 않게 지었다(`a.b`와 `a.b.c`가 같이 있지 않다). [결정] 줄도 들어 있으니, 쓰지 않기로 한 안의 키는 화면에서 부르지 않는다.

```json
{
  "signup.nickname.label": "닉네임",
  "signup.nickname.help": "닉네임에는 실명을 쓰지 말아 주십시오. 학번, 연락처처럼 본인을 알아볼 수 있는 정보도 넣지 말아 주십시오.",
  "signup.password.label": "비밀번호",
  "signup.password.help": "비밀번호는 원래 글자로 되돌릴 수 없는 방식으로 바꿔 저장합니다.",
  "signup.password.noRecovery": "비밀번호 찾기 기능이 없습니다. 비밀번호를 잊으면 계정을 되찾을 수 없습니다.",
  "consent.required.title": "개인정보 수집·이용 동의 (필수)",
  "consent.required.intro": "맞춤 공지 추천과 알림을 드리려면 아래 정보가 필요합니다. 읽어 보신 뒤 동의 여부를 골라 주십시오.",
  "consent.required.purpose.label": "수집·이용 목적",
  "consent.required.purpose.body": "관심 분야와 이력 태그에 맞춘 공지 추천과 알림",
  "consent.required.items.label": "수집 항목",
  "consent.required.items.body": "닉네임, 비밀번호(되돌릴 수 없는 방식으로 바꿔 저장), 학과, 학년, 관심 분야, 관심 키워드, 추천 태그, 알림 등록 정보(알림을 받을 곳을 가리키는 값)",
  "consent.required.retention.label": "보유·이용 기간",
  "consent.required.retention.body": "탈퇴할 때까지 보관합니다. 탈퇴하면 바로 삭제합니다.",
  "consent.required.refuse.label": "동의를 거부할 권리와 불이익",
  "consent.required.refuse.body": "동의를 거부할 수 있습니다. 동의하지 않아도 공지 목록은 볼 수 있습니다. 맞춤 추천과 알림은 받을 수 없습니다.",
  "consent.required.excluded": "이름, 연락처, 학번 같은 지원용 정보는 이 동의의 수집 항목이 아닙니다. 이 서비스의 서버는 그 정보를 받지 않습니다.",
  "consent.required.checkbox": "[필수] 위 내용을 읽었고, 개인정보 수집·이용에 동의합니다.",
  "consent.required.agree": "동의하고 계속",
  "consent.required.decline": "동의하지 않음",
  "consent.required.declineDialog.title": "동의하지 않고 넘어가시겠습니까?",
  "consent.required.declineDialog.body": "공지 목록은 계속 볼 수 있습니다. 맞춤 추천과 알림은 받을 수 없습니다.",
  "consent.required.declineDialog.noAccount": "계정은 만들어지지 않습니다. 나중에 다시 가입할 수 있습니다.",
  "consent.required.declineDialog.accountDeleted": "방금 만든 계정은 바로 삭제됩니다. 나중에 다시 가입할 수 있습니다.",
  "consent.required.declineDialog.confirm": "동의하지 않고 공지 목록 보기",
  "consent.required.declineDialog.cancel": "돌아가기",
  "consent.optional.title": "포트폴리오 분석 동의 (선택)",
  "consent.optional.intro": "포트폴리오 PDF를 올리면 AI가 활동, 수상, 기술을 뽑아 내 이력 칸을 채웁니다. 이 기능을 쓸 때만 동의를 받습니다.",
  "consent.optional.purpose.label": "수집·이용 목적",
  "consent.optional.purpose.body": "포트폴리오에서 활동, 수상, 기술을 뽑아 내 이력 칸 채우기",
  "consent.optional.items.label": "수집 항목",
  "consent.optional.items.body": "올린 PDF에서 뽑은 글. 전화번호, 이메일, 학번 형태의 글자는 보내기 전에 이 기기에서 가립니다.",
  "consent.optional.retention.label": "보유·이용 기간",
  "consent.optional.retention.body": "이 서비스의 서버는 PDF 원본과 보낸 글을 저장하지 않습니다. 분석이 끝나면 버립니다. 분석 결과(활동, 수상, 기술)는 확인을 거쳐 이 기기에만 저장합니다. 확인을 거친 추천 태그만 서버에 저장합니다.",
  "consent.optional.refuse.label": "동의를 거부할 권리와 불이익",
  "consent.optional.refuse.body": "동의를 거부할 수 있습니다. 거부하면 PDF 분석 없이 이력을 직접 입력합니다. 다른 기능은 그대로 쓸 수 있습니다.",
  "consent.optional.externalAi.label": "외부 AI 서비스 이용",
  "consent.optional.externalAi.body": "분석을 위해, 가린 글을 외부 AI 서비스({aiServiceName})로 보냅니다.",
  "consent.optional.checkbox": "[선택] 위 내용을 읽었고, 포트폴리오 분석에 동의합니다.",
  "consent.optional.agree": "동의하고 PDF 올리기",
  "consent.optional.decline": "동의하지 않고 직접 입력하기",
  "consent.optional.warn.name": "이름과 생년월일은 자동으로 가려지지 않습니다. 올리기 전에 PDF에서 지우거나, 지운 사본을 올려 주십시오.",
  "consent.optional.warn.maskLimit": "자동 가리기는 전화번호, 이메일, 학번 형태의 글자만 찾습니다. 다른 형태로 적힌 개인정보는 가려지지 않을 수 있습니다.",
  "consent.optional.warn.scan": "스캔한 이미지로 된 PDF는 글자를 뽑을 수 없습니다. 이때는 이력을 직접 입력해 주십시오.",
  "consent.optional.review": "분석 결과는 바로 저장되지 않습니다. 내용을 확인하고 고친 뒤 저장해 주십시오.",
  "applyInfo.title": "내 지원 정보",
  "applyInfo.notice.local": "이 정보는 이 기기(브라우저)에만 저장되고, 서버로 보내지 않습니다.",
  "applyInfo.notice.noAi": "AI 서비스로도 보내지 않습니다. 지원 준비 화면에서 내 값을 채우는 일은 이 기기 안에서 합니다.",
  "applyInfo.notice.loss": "기기를 바꾸거나 브라우저 데이터를 지우면 이 정보도 사라집니다. 다른 기기로 옮기는 기능은 없습니다.",
  "applyInfo.notice.sharedDevice": "여러 사람이 함께 쓰는 기기에서는 입력하지 말아 주십시오.",
  "applyInfo.notice.notCollected": "주민등록번호와 주소는 받지 않습니다.",
  "applyInfo.notice.copyOnly": "복사 버튼은 값을 복사만 합니다. 다른 사이트의 지원서에 자동으로 입력하거나 대신 제출하지 않습니다.",
  "withdraw.title": "탈퇴",
  "withdraw.body.server": "탈퇴하면 서버에 있는 내 정보를 바로 삭제합니다. 닉네임, 비밀번호 정보, 학과, 학년, 관심 분야, 관심 키워드, 추천 태그, 알림 등록 정보, 동의 기록이 대상입니다.",
  "withdraw.body.irreversible": "삭제한 정보는 되돌릴 수 없습니다.",
  "withdraw.body.device": "이 기기에 저장한 내 지원 정보와 내 이력은 서버에 없어서, 탈퇴만으로는 지워지지 않습니다.",
  "withdraw.deviceCheckbox": "이 기기에 저장한 내 지원 정보와 내 이력도 함께 지우기",
  "withdraw.confirm": "탈퇴하기",
  "withdraw.cancel": "취소",
  "withdraw.done.message": "탈퇴했습니다. 서버에 있던 내 정보를 삭제했습니다.",
  "withdraw.done.deviceKept": "이 기기에 저장한 정보는 남아 있습니다. 지우려면 브라우저에서 이 사이트의 데이터를 삭제해 주십시오.",
  "onboarding.nlInput.notice": "이 칸에 쓴 문장은 구독 조건으로 바꾸기 위해 외부 AI 서비스({aiServiceName})로 보냅니다. 이름, 연락처, 학번은 쓰지 말아 주십시오."
}
```
