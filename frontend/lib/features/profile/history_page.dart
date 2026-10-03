import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/subscription_api.dart';
import 'package:kmu_notice/shared/lib/catalog.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/mascot_guide.dart';
import 'package:kmu_notice/shared/ui/select_chip.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';
import 'entry_list_editor.dart';
import 'local_only_notice.dart';
import 'profile_store.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  ProfileHistory? _h;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    ProfileStore.load().then((h) => setState(() => _h = h));
  }

  List<String> _titles(List<Map<String, dynamic>> l) =>
      l.map((e) => e['title'] as String).toList();

  List<Map<String, dynamic>> _entries(List<String> titles) =>
      titles.map((t) => <String, dynamic>{'title': t}).toList();

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      await ProfileStore.save(_h!);
      await SubscriptionApi.saveTags(_h!.tags);
      if (mounted) context.go(Routes.feed);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  void _toggleTag(String t) => setState(
        () => _h!.tags.contains(t) ? _h!.tags.remove(t) : _h!.tags.add(t),
      );

  void _replace(List<Map<String, dynamic>> target, List<String> titles) =>
      setState(() => target
        ..clear()
        ..addAll(_entries(titles)));

  @override
  Widget build(BuildContext context) {
    final h = _h;
    if (h == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return StepScaffold(
      guide: const MascotGuide(
        'PDF가 있으면 이력을 대신 채워 볼게요.\n나중에 채워도 괜찮아요.',
      ),
      title: '내 이력을 알려 주시면\n맞는 공고를 골라 드려요',
      ctaLabel: h.tags.isEmpty ? '나중에 할게요' : '저장하고 피드 보기',
      ctaLoading: _saving,
      onCta: _save,
      children: [
        const LocalOnlyNotice(),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => context.push(Routes.portfolio),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: const Text('포트폴리오 PDF로 채우기'),
          style: OutlinedButton.styleFrom(
            minimumSize: const Size.fromHeight(48),
            side: const BorderSide(color: AppColors.grey300),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
        const SizedBox(height: 28),
        const Text(
          '관심 태그',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w600,
            color: AppColors.grey700,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final t in Catalog.tags)
              SelectChip(
                label: t,
                selected: h.tags.contains(t),
                onTap: () => _toggleTag(t),
              ),
          ],
        ),
        const SizedBox(height: 32),
        EntryListEditor(
          label: '기술',
          hint: '예: Python, Figma',
          items: h.skills,
          onChanged: (v) => setState(() => h.skills
            ..clear()
            ..addAll(v)),
        ),
        EntryListEditor(
          label: '프로젝트',
          hint: '프로젝트 이름',
          items: _titles(h.projects),
          onChanged: (v) => _replace(h.projects, v),
        ),
        EntryListEditor(
          label: '수상',
          hint: '수상 이름',
          items: _titles(h.awards),
          onChanged: (v) => _replace(h.awards, v),
        ),
        EntryListEditor(
          label: '대외활동',
          hint: '활동 이름',
          items: _titles(h.activities),
          onChanged: (v) => _replace(h.activities, v),
        ),
      ],
    );
  }
}
