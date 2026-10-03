import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/auth_api.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

import 'info_dialogs.dart';

// 헤더 오른쪽 안내 메뉴. 넓으면 글자 버튼 셋, 좁으면 메뉴 하나로 접는다.
class InfoNav extends StatelessWidget {
  const InfoNav({super.key, required this.collapsed, required this.notices});
  final bool collapsed;
  final List<Notice> notices;

  static const _items = {
    'how': '추천 방식',
    'sources': '수집 출처',
    'try': '사용해 보기',
  };

  @override
  Widget build(BuildContext context) {
    if (collapsed) {
      return PopupMenuButton<String>(
        tooltip: '안내',
        icon: const Icon(Icons.menu_rounded),
        onSelected: (key) => _open(context, key),
        itemBuilder: (_) => [
          for (final e in _items.entries)
            PopupMenuItem<String>(value: e.key, child: Text(e.value)),
        ],
      );
    }
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (final e in _items.entries)
          TextButton(
            onPressed: () => _open(context, e.key),
            style: TextButton.styleFrom(
              foregroundColor: AppColors.grey700,
              textStyle: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
              ),
            ),
            child: Text(e.value),
          ),
        const SizedBox(width: 8),
      ],
    );
  }

  void _open(BuildContext context, String key) {
    switch (key) {
      case 'how':
        showRecommendInfo(context);
      case 'sources':
        showSourceInfo(context, notices);
      default:
        // 로그인 전에는 가입·로그인 첫 화면, 로그인 뒤에는 관심 분야 고르기로 보낸다.
        context.push(
          AuthApi.isLoggedIn ? Routes.onboardingInterests : Routes.welcome,
        );
    }
  }
}
