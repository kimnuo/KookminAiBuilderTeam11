import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

import 'app/router.dart';
import 'shared/ui/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  if (kIsWeb) WidgetsBinding.instance.ensureSemantics();
  runApp(const KmuNoticeApp());
}

class KmuNoticeApp extends StatelessWidget {
  const KmuNoticeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: '크노 · 국민대 소식 대시보드',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      routerConfig: appRouter,
    );
  }
}
