import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/auth_api.dart';
import 'package:kmu_notice/shared/api/profile_api.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/consent_check_row.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';
import 'info_box.dart';
import 'masked_preview.dart';
import 'pdf_text_extractor.dart';
import 'pii_masker.dart';
import 'portfolio_consent_texts.dart';
import 'profile_analysis.dart';
import 'warning_box.dart';

class PortfolioPage extends StatefulWidget {
  const PortfolioPage({super.key});

  @override
  State<PortfolioPage> createState() => _PortfolioPageState();
}

class _PortfolioPageState extends State<PortfolioPage> {
  bool _agreed = false;
  bool _busy = false;
  MaskResult? _masked;
  String? _error;

  Future<void> _run(Future<void> Function() task) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await task();
    } catch (_) {
      setState(() => _error = '처리하지 못했어요. 잠시 후 다시 시도해 주세요.');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _pickAndMask() => _run(() async {
        final files = await FilePicker.pickFiles(
          type: FileType.custom,
          allowedExtensions: ['pdf'],
        );
        if (files.isEmpty) return;
        final text = await PdfTextExtractor.extract(
          await files.first.readAsBytes(),
        );
        if (text.isEmpty) {
          setState(() => _error = '글자를 읽을 수 없는 PDF예요(스캔 이미지일 수 있어요). '
              '이력을 직접 입력해 주세요.');
          return;
        }
        setState(() => _masked = PiiMasker.mask(text));
      });

  Future<void> _analyze() => _run(() async {
        await AuthApi.recordConsent(portfolio: true);
        final res = await ProfileApi.analyze(_masked!.text);
        final analysis = ProfileAnalysis.fromJson(res);
        if (!mounted) return;
        if (analysis.isEmpty) {
          setState(() => _error = '근거가 확인된 이력을 찾지 못했어요. 직접 입력해 주세요.');
          return;
        }
        context.pushReplacement(Routes.portfolioReview, extra: analysis);
      });

  @override
  Widget build(BuildContext context) {
    final masked = _masked;
    return StepScaffold(
      title: masked == null ? '포트폴리오 PDF로\n이력을 채워 드릴게요' : '이 내용으로\n분석할까요?',
      ctaLabel: masked == null ? 'PDF 고르기' : '분석하기',
      ctaLoading: _busy,
      onCta: masked != null ? _analyze : (_agreed ? _pickAndMask : null),
      children: [
        if (masked == null) ..._intro() else MaskedPreview(result: masked),
        if (_error != null) ...[
          const SizedBox(height: 16),
          Text(_error!, style: const TextStyle(color: AppColors.danger)),
        ],
      ],
    );
  }

  List<Widget> _intro() => [
        const WarningBox(
          '이름과 생년월일은 자동으로 가려지지 않아요. '
          '올리기 전에 PDF에서 지워 주세요.',
        ),
        const SizedBox(height: 16),
        const InfoBox(rows: portfolioConsentRows),
        const SizedBox(height: 16),
        ConsentCheckRow(
          label: '[선택] 포트폴리오 분석에 동의해요',
          checked: _agreed,
          onTap: () => setState(() => _agreed = !_agreed),
        ),
      ];
}
