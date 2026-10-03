import 'package:flutter/material.dart';

import 'app/router.dart';
import 'shared/ui/app_theme.dart';

void main() {
  runApp(const KmuNoticeApp());
}

class KmuNoticeApp extends StatelessWidget {
  const KmuNoticeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: '국민대 공지 알림',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      routerConfig: appRouter,
    );
  }
}
