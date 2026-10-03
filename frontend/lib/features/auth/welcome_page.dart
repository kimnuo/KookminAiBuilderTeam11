import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/lib/feed_path.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/bottom_cta.dart';
import 'package:kmu_notice/shared/ui/mascot_guide.dart';

/// 처음 오는 사람이 보는 화면. 넓은 화면에서도 글과 버튼이 가운데 420px 안에 모인다
/// (2026-10-03: 좌측에 붙고 버튼이 화면 끝까지 늘어지던 문제).
const _maxWidth = 420.0;

class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: _maxWidth),
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 64, 24, 24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  MascotGuide(
                    '안녕하세요, 크노예요.\n흩어진 학교 공지를 대신 읽어 드릴게요.',
                    size: 72,
                  ),
                  SizedBox(height: 28),
                  Text(
                    '흩어진 학교 공지,\n나한테 맞는 것만',
                    style: TextStyle(
                      fontSize: 30,
                      fontWeight: FontWeight.w700,
                      height: 1.35,
                    ),
                  ),
                  SizedBox(height: 12),
                  Text(
                    '본부·단과대 공지와 공모전 소식을\nAI가 골라서 알려 드려요.',
                    style: TextStyle(
                      fontSize: 17,
                      height: 1.5,
                      color: AppColors.grey700,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        // Center 를 쓰면 하단 바가 세로로 화면 전체를 먹어 본문이 사라진다.
        // Align + heightFactor 1 은 가로만 가운데로 모으고 높이는 자식에 맞춘다 (2026-10-03)
        child: Align(
          alignment: Alignment.bottomCenter,
          heightFactor: 1,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: _maxWidth),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                BottomCta(
                  label: '시작하기',
                  onPressed: () => context.push(Routes.signup),
                ),
                TextButton(
                  onPressed: () => context.push(Routes.login),
                  child: const Text(
                    '이미 계정이 있어요',
                    style: TextStyle(fontSize: 15, color: AppColors.grey700),
                  ),
                ),
                TextButton(
                  onPressed: () => context.go(feedPath),
                  child: const Text(
                    '로그인 없이 둘러볼게요',
                    style: TextStyle(fontSize: 14, color: AppColors.grey500),
                  ),
                ),
                const SizedBox(height: 8),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
