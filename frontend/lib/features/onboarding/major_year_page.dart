import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/lib/catalog.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/select_chip.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';
import 'onboarding_draft.dart';
import 'section_label.dart';

class MajorYearPage extends StatefulWidget {
  const MajorYearPage({super.key});

  @override
  State<MajorYearPage> createState() => _MajorYearPageState();
}

class _MajorYearPageState extends State<MajorYearPage> {
  String? _major = OnboardingDraft.major;
  int? _year = OnboardingDraft.year;

  void _next() {
    OnboardingDraft.major = _major;
    OnboardingDraft.year = _year;
    context.push(Routes.onboardingInterests);
  }

  @override
  Widget build(BuildContext context) {
    return StepScaffold(
      title: '학과와 학년을\n알려 주세요',
      subtitle: '나에게 해당하는 공지를 먼저 보여 드려요.',
      ctaLabel: '다음',
      onCta: _major != null && _year != null ? _next : null,
      children: [
        const SectionLabel('학년'),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final y in Catalog.subscriptionYears)
              SelectChip(
                label: Catalog.yearLabel(y),
                selected: _year == y,
                onTap: () => setState(() => _year = y),
              ),
          ],
        ),
        const SizedBox(height: 32),
        const SectionLabel('학과'),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final m in Catalog.majors)
              SelectChip(
                label: m,
                selected: _major == m,
                onTap: () => setState(() => _major = m),
              ),
          ],
        ),
      ],
    );
  }
}
