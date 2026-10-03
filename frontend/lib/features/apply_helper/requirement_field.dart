import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

class RequirementField extends StatelessWidget {
  const RequirementField({super.key, required this.field, required this.value});
  final Map<String, dynamic> field;
  final String value;
  @override
  Widget build(BuildContext context) => Card(
    elevation: 0,
    color: AppColors.surface,
    margin: const EdgeInsets.only(bottom: 10),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  '${FeedConfig.fieldLabels[field['key']] ?? field['label']} · ${field['required'] == true ? '필수' : '선택'}',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              ),
              TextButton.icon(
                onPressed: value.isEmpty ? null : () => _copy(context),
                icon: const Icon(Icons.copy_rounded, size: 16),
                label: const Text('복사'),
              ),
            ],
          ),
          SelectableText(value.isEmpty ? '내 지원 정보에 입력해 주세요.' : value),
          const SizedBox(height: 8),
          Text(
            '근거: ${field['evidence']}',
            style: const TextStyle(
              fontSize: 12,
              height: 1.5,
              color: AppColors.grey700,
            ),
          ),
        ],
      ),
    ),
  );
  Future<void> _copy(BuildContext context) async {
    try {
      await Clipboard.setData(ClipboardData(text: value));
      if (context.mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('지원 정보를 복사했어요.')));
      }
    } catch (_) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('복사하지 못했어요. 값을 직접 선택해 주세요.')),
        );
      }
    }
  }
}
