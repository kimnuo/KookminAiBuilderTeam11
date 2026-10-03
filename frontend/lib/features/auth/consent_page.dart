import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/auth_api.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/consent_check_row.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';
import 'consent_texts.dart';

class ConsentPage extends StatefulWidget {
  const ConsentPage({super.key});

  @override
  State<ConsentPage> createState() => _ConsentPageState();
}

class _ConsentPageState extends State<ConsentPage> {
  bool _agreed = false;
  bool _loading = false;

  Future<void> _submit() async {
    setState(() => _loading = true);
    try {
      await AuthApi.recordConsent(portfolio: false);
      if (mounted) context.go(Routes.onboardingMajor);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return StepScaffold(
      title: '맞춤 알림을 위해\n동의가 필요해요',
      subtitle: '이름, 연락처, 학번은 서버에 저장하지 않아요.',
      ctaLabel: '동의하고 계속하기',
      ctaLoading: _loading,
      onCta: _agreed ? _submit : null,
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (final (label, body) in requiredConsentRows) ...[
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 13,
                    color: AppColors.grey500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(body, style: const TextStyle(fontSize: 15, height: 1.5)),
                const SizedBox(height: 16),
              ],
            ],
          ),
        ),
        const SizedBox(height: 16),
        ConsentCheckRow(
          label: '[필수] 개인정보 수집·이용에 동의해요',
          checked: _agreed,
          onTap: () => setState(() => _agreed = !_agreed),
        ),
        const SizedBox(height: 8),
        TextButton(
          onPressed: () => context.go(Routes.feed),
          child: const Text(
            '동의하지 않고 공지만 볼게요',
            style: TextStyle(color: AppColors.grey500),
          ),
        ),
      ],
    );
  }
}
