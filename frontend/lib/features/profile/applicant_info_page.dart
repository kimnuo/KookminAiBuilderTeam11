import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/lib/applicant_store.dart';
import 'package:kmu_notice/shared/lib/catalog.dart';
import 'package:kmu_notice/shared/ui/app_text_field.dart';
import 'package:kmu_notice/shared/ui/select_chip.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';
import 'local_only_notice.dart';
import 'section_title.dart';

const _fields = [
  ('name', '이름', '김예시'),
  ('phone', '연락처', '010-0000-0000'),
  ('email', '이메일', 'example@example.com'),
  ('studentId', '학번', '8자리'),
  ('school', '학교', '국민대학교'),
  ('major', '학과', '소프트웨어학부'),
  ('birthDate', '생년월일', '2004-01-01'),
  ('portfolioUrl', '포트폴리오 링크', 'https://'),
];

class ApplicantInfoPage extends StatefulWidget {
  const ApplicantInfoPage({super.key});

  @override
  State<ApplicantInfoPage> createState() => _ApplicantInfoPageState();
}

class _ApplicantInfoPageState extends State<ApplicantInfoPage> {
  final _controllers = {
    for (final (key, _, _) in _fields) key: TextEditingController(),
  };
  String? _year;
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    ApplicantStore.load().then((info) {
      if (!mounted) return;
      for (final e in _controllers.entries) {
        e.value.text = info[e.key] ?? '';
      }
      setState(() {
        _year = info['year'];
        _loaded = true;
      });
    });
  }

  Future<void> _save() async {
    String? clean(String v) => v.trim().isEmpty ? null : v.trim();
    await ApplicantStore.save(ApplicantInfo({
      for (final e in _controllers.entries) e.key: clean(e.value.text),
      'year': _year,
    }));
    if (mounted) context.pop();
  }

  @override
  Widget build(BuildContext context) {
    if (!_loaded) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return StepScaffold(
      title: '지원할 때마다 쓰는 정보를\n한 번만 적어 두세요',
      subtitle: '공고별로 필요한 칸을 골라 복사할 수 있어요.',
      ctaLabel: '저장',
      onCta: _save,
      children: [
        const LocalOnlyNotice(
          text: '이 정보는 이 기기에만 저장되고 서버로 보내지 않아요.',
        ),
        const SizedBox(height: 28),
        for (final (key, label, hint) in _fields)
          AppTextField(label: label, controller: _controllers[key]!, hint: hint),
        const SectionTitle('학년'),
        Wrap(
          spacing: 8,
          children: [
            for (final y in Catalog.years)
              SelectChip(
                label: '$y학년',
                selected: _year == '$y',
                onTap: () => setState(() => _year = '$y'),
              ),
          ],
        ),
      ],
    );
  }
}
