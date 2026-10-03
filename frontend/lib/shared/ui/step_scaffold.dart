import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'bottom_cta.dart';

class StepScaffold extends StatelessWidget {
  const StepScaffold({
    super.key,
    required this.title,
    this.subtitle,
    required this.children,
    required this.ctaLabel,
    required this.onCta,
    this.ctaLoading = false,
    this.guide,
  });

  // 제목 위에 놓는 안내. 온보딩에서는 MascotGuide를 넣는다.
  final Widget? guide;
  final String title;
  final String? subtitle;
  final List<Widget> children;
  final String ctaLabel;
  final VoidCallback? onCta;
  final bool ctaLoading;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
          children: [
            if (guide != null) ...[guide!, const SizedBox(height: 20)],
            Text(
              title,
              style: const TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.w700,
                height: 1.35,
              ),
            ),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(
                subtitle!,
                style: const TextStyle(fontSize: 16, color: AppColors.grey700),
              ),
            ],
            const SizedBox(height: 32),
            ...children,
          ],
        ),
      ),
      bottomNavigationBar: BottomCta(
        label: ctaLabel,
        onPressed: onCta,
        loading: ctaLoading,
      ),
    );
  }
}
