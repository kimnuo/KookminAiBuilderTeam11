import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/notice_api.dart';
import 'package:kmu_notice/shared/lib/application_values.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

import 'requirements.dart';
import 'requirement_field.dart';
import 'requirement_document.dart';

class ApplyPanel extends StatefulWidget {
  const ApplyPanel({super.key, required this.notice, this.onEdit});
  final Notice notice;
  final Future<void> Function()? onEdit;
  @override
  State<ApplyPanel> createState() => _ApplyPanelState();
}

class _ApplyPanelState extends State<ApplyPanel> {
  late Future<Map<String, dynamic>> _requirements;
  late Future<Map<String, String>> _values;
  @override
  void initState() {
    super.initState();
    _requirements = NoticeApi.requirements(widget.notice.id);
    _values = applicationValues();
  }

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        children: [
          const Expanded(
            child: Text(
              '지원 준비',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
            ),
          ),
          if (!FeedConfig.demo)
            TextButton(onPressed: _edit, child: const Text('내 지원 정보 수정')),
        ],
      ),
      const Text(
        '내 값은 이 기기에만 저장되며 서버와 AI로 보내지 않아요.',
        style: TextStyle(fontSize: 12, color: AppColors.grey500),
      ),
      const SizedBox(height: 16),
      FutureBuilder(
        future: _requirements,
        builder: (_, snapshot) {
          if (snapshot.hasError) {
            return const Text('준비 목록을 불러오지 못했어요. 원문에서 확인해 주세요.');
          }
          if (!snapshot.hasData) return const LinearProgressIndicator();
          return FutureBuilder(
            future: _values,
            builder: (_, values) => _content(snapshot.data!, values.data ?? {}),
          );
        },
      ),
    ],
  );

  Widget _content(Map<String, dynamic> data, Map<String, String> values) {
    final fields = requirementFields(data),
        documents = requirementDocuments(data);
    final actions = requirementActions(data, widget.notice);
    if (fields.isEmpty && documents.isEmpty && actions.isEmpty) {
      if (data['status'] == 'unavailable') {
        return const Text('필요한 항목은 공고의 필수 사항과 원문에서 확인해 주세요.');
      }
      return const Text('근거가 있는 준비 목록이 없어요. 원문을 확인해 주세요.');
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ...fields.map(
          (f) => RequirementField(field: f, value: values[f['key']] ?? ''),
        ),
        if (documents.isNotEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 16),
            child: Text('필요 서류', style: TextStyle(fontWeight: FontWeight.w700)),
          ),
        ...documents.map((d) => RequirementDocument(document: d)),
        if (actions.isNotEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 16),
            child: Text(
              '필수 준비 사항',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
        ...actions.map((a) => RequirementDocument(document: a)),
      ],
    );
  }

  Future<void> _edit() async {
    if (widget.onEdit != null) {
      await widget.onEdit!();
      return;
    }
    await context.push(Routes.applicantInfo);
    if (mounted) setState(() => _values = applicationValues());
  }
}
