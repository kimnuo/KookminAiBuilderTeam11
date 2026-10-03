class SignupRules {
  static const nicknameMin = 2;
  static const nicknameMax = 12;
  static const passwordMin = 8;

  static bool nicknameLength(String v) {
    final t = v.trim();
    return t.length >= nicknameMin && t.length <= nicknameMax;
  }

  static bool passwordLength(String v) => v.length >= passwordMin;
  static bool hasLetter(String v) => RegExp(r'[A-Za-z]').hasMatch(v);
  static bool hasDigit(String v) => RegExp(r'[0-9]').hasMatch(v);

  static bool passwordValid(String v) =>
      passwordLength(v) && hasLetter(v) && hasDigit(v);
}
