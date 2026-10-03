import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

// 민섭(features/feed)의 피드 화면이 들어오면 router.dart에서 교체하고 이 파일은 지운다.
// 피드 상단에도 설정(Routes.settings)으로 가는 버튼을 둬야 한다.
class FeedPlaceholderPage extends StatelessWidget {
  const FeedPlaceholderPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: [
          IconButton(
            tooltip: '설정',
            icon: const Icon(Icons.settings_rounded, color: AppColors.grey700),
            onPressed: () => context.push(Routes.settings),
          ),
        ],
      ),
      body: const Center(
        child: Text(
          '피드 화면 자리 (프론트 B)',
          style: TextStyle(fontSize: 16, color: AppColors.grey500),
        ),
      ),
    );
  }
}
