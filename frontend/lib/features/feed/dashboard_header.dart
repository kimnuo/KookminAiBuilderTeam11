import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/auth_api.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/routes.dart';

import 'info_nav.dart';
import 'kno_home_button.dart';

class DashboardHeader extends StatelessWidget {
  const DashboardHeader({
    super.key,
    required this.compact,
    required this.onHome,
    required this.notices,
  });
  final bool compact;
  final VoidCallback onHome;
  final List<Notice> notices;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, size) => _row(context, size.maxWidth),
  );

  // 안내 메뉴 글자 버튼 셋이 들어갈 폭이 안 되면 메뉴 하나로 접는다.
  Widget _row(BuildContext context, double width) => Row(
    children: [
      KnoHomeButton(onPressed: onHome),
      if (!compact) ...[
        const SizedBox(width: 24),
        const Text(
          '학교 소식과 기회, 한눈에',
          style: TextStyle(fontSize: 21, fontWeight: FontWeight.w600),
        ),
      ],
      const Spacer(),
      InfoNav(collapsed: compact || width < 900, notices: notices),
      // 로그인 전에도 공지는 다 보인다. 가입·로그인 입구만 여기 둔다.
      // 좁은 화면에서는 글자 버튼이 헤더를 넘치게 해서(320px) 아이콘으로 바꾼다.
      ValueListenableBuilder<bool>(
        valueListenable: AuthApi.loggedIn,
        builder: (context, loggedIn, _) =>
            loggedIn ? const SizedBox.shrink() : _loginEntry(context),
      ),
      IconButton(
        tooltip: '내 지원 정보',
        icon: const Icon(Icons.person_outline_rounded),
        onPressed: () => context.push(Routes.applicantInfo),
      ),
      IconButton(
        tooltip: '설정',
        icon: const Icon(Icons.settings_outlined),
        onPressed: () => context.push(Routes.settings),
      ),
    ],
  );

  Widget _loginEntry(BuildContext context) {
    void open() => context.push(Routes.welcome);
    if (compact) {
      return IconButton(
        tooltip: '로그인',
        icon: const Icon(Icons.login_rounded),
        onPressed: open,
      );
    }
    return TextButton(onPressed: open, child: const Text('로그인'));
  }
}
