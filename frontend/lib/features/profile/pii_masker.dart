class MaskResult {
  const MaskResult(this.text, this.counts);
  final String text;
  final Map<String, int> counts;

  int get total => counts.values.fold(0, (a, b) => a + b);
}

// PDF 글을 AI로 보내기 전에 이 기기에서 가린다. 이름·생년월일은 자동으로 못 가린다.
class PiiMasker {
  static final _rules = <String, RegExp>{
    '이메일': RegExp(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
    '전화번호': RegExp(
      r'(\+82[-\s.]?)?\(?0\d{1,2}\)?[-\s.]?\d{3,4}[-\s.]?\d{4}(?!\d)',
    ),
    '학번': RegExp(r'(?<!\d)(19|20)\d{6}(?!\d)'),
  };

  static MaskResult mask(String input) {
    var text = input;
    final counts = <String, int>{};
    for (final entry in _rules.entries) {
      var n = 0;
      text = text.replaceAllMapped(entry.value, (_) {
        n++;
        return '[${entry.key}]';
      });
      counts[entry.key] = n;
    }
    return MaskResult(text, counts);
  }
}
