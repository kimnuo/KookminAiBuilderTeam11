// 프론트 참조용 (택준). 브라우저에서 PDF 글자를 뽑은 뒤 AI로 보내기 전에 가린다.
// 패턴은 backend/app/ai/config/mask_patterns.json 을 그대로 쓴다. 규칙을 바꿀 때는 JSON 만 고친다.
// 파이썬 app/ai/mask.py 의 mask_contacts 와 같은 결과를 내야 한다(패턴 순서, keep 처리가 같다).
// 서버도 AI를 부르기 전에 한 번 더 가린다. 이 코드는 "기기 밖으로 나가기 전에" 가리는 첫 번째 단계다.
//
// 쓰는 법
//   import patterns from "./mask_patterns.json";
//   const compiled = compileMaskPatterns(patterns);
//   const { text, count } = maskContacts(pdfText, compiled);
//   // count 를 화면에 보여 준다: "전화번호·이메일·학번 3곳을 가렸습니다"
//   // 이름·생년월일·개인 사이트 주소는 못 가린다는 안내도 같이 보여 준다.

export function compileMaskPatterns(config) {
  return config.patterns.map((p) => ({
    keep: p.keep || 0,
    replace: p.replace,
    re: new RegExp(p.regex, "g"),
  }));
}

export function maskContacts(text, compiled) {
  let out = text || "";
  let count = 0;
  for (const p of compiled) {
    out = out.replace(p.re, (...args) => {
      count += 1;
      const kept = p.keep ? args[p.keep] || "" : "";
      return kept + p.replace;
    });
  }
  return { text: out, count };
}
