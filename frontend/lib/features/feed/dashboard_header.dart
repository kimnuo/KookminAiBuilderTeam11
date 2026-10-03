import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

class DashboardHeader extends StatelessWidget {
  const DashboardHeader({super.key, required this.compact});
  final bool compact;
  @override
  Widget build(BuildContext context) => Row(
    children: [
      const Icon(Icons.blur_on_rounded, color: AppColors.primary, size: 30),
      const SizedBox(width: 8),
      const Text(
        '크노',
        style: TextStyle(fontSize: 25, fontWeight: FontWeight.w700),
      ),
      if (!compact) ...[
        const SizedBox(width: 24),
        const Text(
          '학교 소식과 기회, 한눈에',
          style: TextStyle(fontSize: 21, fontWeight: FontWeight.w600),
        ),
      ],
      const Spacer(),
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
}
