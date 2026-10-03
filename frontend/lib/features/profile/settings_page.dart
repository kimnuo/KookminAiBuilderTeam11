import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/auth_api.dart';
import 'package:kmu_notice/shared/lib/applicant_store.dart';
import 'package:kmu_notice/shared/lib/interest_store.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'profile_store.dart';
import 'settings_tile.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  Future<void> _logout(BuildContext context) async {
    await AuthApi.logout();
    if (context.mounted) context.go(Routes.welcome);
  }

  Future<void> _withdraw(BuildContext context) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('정말 탈퇴할까요?'),
        content: const Text('서버에 있는 내 정보와 이 기기에 저장한 이력·지원 정보를 모두 지워요.'),
        actions: [
          TextButton(
            onPressed: () => c.pop(false),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () => c.pop(true),
            child: const Text('탈퇴', style: TextStyle(color: AppColors.danger)),
          ),
        ],
      ),
    );
    if (ok != true) return;
    await AuthApi.deleteMe();
    await ProfileStore.clear();
    await ApplicantStore.clear();
    await InterestStore.clear();
    if (context.mounted) context.go(Routes.welcome);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          '설정',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
        ),
      ),
      body: ListView(
        children: [
          SettingsTile(
            label: '관심 분야 바꾸기',
            onTap: () => context.push(Routes.onboardingMajor),
          ),
          SettingsTile(
            label: '내 이력',
            onTap: () => context.push(Routes.profileHistory),
          ),
          SettingsTile(
            label: '포트폴리오 PDF로 이력 채우기',
            onTap: () => context.push(Routes.portfolio),
          ),
          SettingsTile(
            label: '내 지원 정보',
            onTap: () => context.push(Routes.applicantInfo),
          ),
          const Divider(height: 32, thickness: 8, color: AppColors.surface),
          SettingsTile(label: '로그아웃', onTap: () => _logout(context)),
          SettingsTile(
            label: '탈퇴하기',
            danger: true,
            onTap: () => _withdraw(context),
          ),
        ],
      ),
    );
  }
}
