import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/subscription_api.dart';
import 'package:kmu_notice/shared/lib/catalog.dart';
import 'package:kmu_notice/shared/lib/interest_store.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/select_chip.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';
import 'natural_language_box.dart';
import 'onboarding_draft.dart';
import 'section_label.dart';

class InterestsPage extends StatefulWidget {
  const InterestsPage({super.key});

  @override
  State<InterestsPage> createState() => _InterestsPageState();
}

class _InterestsPageState extends State<InterestsPage> {
  final _text = TextEditingController();
  final Set<String> _selected = {};
  List<String> _keywords = [];
  bool _parsing = false;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    // 설정의 「관심 분야 바꾸기」로 다시 오면 저장해 둔 분야를 켜 둔다.
    InterestStore.load().then((saved) {
      if (!mounted) return;
      setState(
        () => _selected.addAll(saved.where(Catalog.categories.contains)),
      );
    });
  }

  Future<void> _parse() async {
    if (_text.text.trim().isEmpty) return;
    setState(() => _parsing = true);
    try {
      final res = await SubscriptionApi.parse(_text.text.trim());
      final cats = List<String>.from(res['categories'] ?? const []);
      setState(() {
        _selected.addAll(cats.where(Catalog.categories.contains));
        _keywords = List<String>.from(res['keywords'] ?? const []);
      });
    } finally {
      if (mounted) setState(() => _parsing = false);
    }
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      await InterestStore.save(_selected.toList());
      await SubscriptionApi.save(
        major: OnboardingDraft.major!,
        year: OnboardingDraft.year!,
        categories: _selected.toList(),
        keywords: _keywords,
      );
      if (mounted) context.go(Routes.profileHistory);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  void _toggle(String c) => setState(
        () => _selected.contains(c) ? _selected.remove(c) : _selected.add(c),
      );

  @override
  Widget build(BuildContext context) {
    return StepScaffold(
      title: '어떤 소식을\n받아 볼까요?',
      subtitle: '고른 분야의 공지만 알려 드려요.',
      ctaLabel: _selected.isEmpty ? '분야를 골라 주세요' : '${_selected.length}개 분야 받기',
      ctaLoading: _saving,
      onCta: _selected.isEmpty ? null : _save,
      children: [
        NaturalLanguageBox(
          controller: _text,
          loading: _parsing,
          onParse: _parse,
        ),
        const SizedBox(height: 32),
        const SectionLabel('관심 분야'),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final c in Catalog.categories)
              SelectChip(
                label: c,
                selected: _selected.contains(c),
                onTap: () => _toggle(c),
              ),
          ],
        ),
      ],
    );
  }
}
