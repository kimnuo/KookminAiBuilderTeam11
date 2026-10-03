class AppConfig {
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  // 백엔드 준비 전까지 true. 실행 시 --dart-define=USE_MOCK=false 로 끈다.
  static const useMock = bool.fromEnvironment('USE_MOCK', defaultValue: true);

  static const consentVersion = '2026-10-03';
}
