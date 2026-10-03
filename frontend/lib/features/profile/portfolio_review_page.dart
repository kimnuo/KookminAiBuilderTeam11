import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/lib/app_config.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/select_chip.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';
import 'profile_analysis.dart';
import 'profile_store.dart';
import 'review_item_card.dart';
import 'section_title.dart';
import 'warning_box.dart';

class PortfolioReviewPage extends StatefulWidget {
  const PortfolioReviewPage({super.key, required this.analysis});

  final ProfileAnalysis analysis;

  @override
  State<PortfolioReviewPage> createState() => _PortfolioReviewPageState();
}

class _PortfolioReviewPageState extends State<PortfolioReviewPage> {
  late final Set<String> _tags = {...widget.analysis.tags};
  late final Set<String> _skills = {...widget.analysis.skills};
  bool _saving = false;

  Future<void> _save() async {
    setState(() => _saving = true);
    final h = await ProfileStore.load();
    _addAll(h.tags, _tags);
    _addAll(h.skills, _skills);
    for (final item in widget.analysis.items.where((i) => i.keep)) {
      final target = switch (item.kind) {
        'projects' => h.projects,
        'awards' => h.awards,
        _ => h.activities,
      };
      if (target.any((e) => e['title'] == item.title)) continue;
      target.add({'title': item.title, 'evidence': item.evidence});
    }
    await ProfileStore.save(h);
    if (mounted) context.go(Routes.profileHistory);
  }

  void _addAll(List<String> target, Set<String> values) =>
      target.addAll(values.where((v) => !target.contains(v)));

  void _toggle(Set<String> set, String v) =>
      setState(() => set.contains(v) ? set.remove(v) : set.add(v));

  @override
  Widget build(BuildContext context) {
    final a = widget.analysis;
    return StepScaffold(
      title: 'AI가 찾은 이력이에요',
      subtitle: '맞는 것만 남기고 저장해 주세요. 이 기기에만 저장돼요.',
      ctaLabel: '내 이력에 저장',
      ctaLoading: _saving,
      onCta: _save,
      children: [
        if (AppConfig.useMock) ...[
          const WarningBox('데모용 예시 결과예요. 올린 PDF 내용과 관계없이 항상 같은 결과가 나와요.'),
          const SizedBox(height: 24),
        ],
        if (a.tags.isNotEmpty) ...[
          const SectionTitle('추천 태그'),
          _chips(a.tags, _tags),
        ],
        if (a.skills.isNotEmpty) ...[
          const SectionTitle('기술'),
          _chips(a.skills, _skills),
        ],
        if (a.items.isNotEmpty) ...[
          const SectionTitle('활동·수상·프로젝트'),
          for (final item in a.items)
            ReviewItemCard(
              item: item,
              onTap: () => setState(() => item.keep = !item.keep),
            ),
        ],
      ],
    );
  }

  Widget _chips(List<String> all, Set<String> selected) => Padding(
        padding: const EdgeInsets.only(bottom: 28),
        child: Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final v in all)
              SelectChip(
                label: v,
                selected: selected.contains(v),
                onTap: () => _toggle(selected, v),
              ),
          ],
        ),
      );
}
