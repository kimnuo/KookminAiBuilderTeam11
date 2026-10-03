import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/bottom_cta.dart';
import 'package:kmu_notice/shared/ui/mascot_guide.dart';

class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: const SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(24, 96, 24, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
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
      bottomNavigationBar: Column(
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
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}
