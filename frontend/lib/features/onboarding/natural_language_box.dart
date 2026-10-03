import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class NaturalLanguageBox extends StatelessWidget {
  const NaturalLanguageBox({
    super.key,
    required this.controller,
    required this.loading,
    required this.onParse,
  });

  final TextEditingController controller;
  final bool loading;
  final VoidCallback onParse;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 4, 8, 4),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          const Icon(Icons.auto_awesome, color: AppColors.primary, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              controller: controller,
              style: const TextStyle(fontSize: 15),
              decoration: const InputDecoration(
                hintText: '예: AI 관련 공모전이랑 장학금',
                hintStyle: TextStyle(color: AppColors.grey500),
                border: InputBorder.none,
              ),
            ),
          ),
          TextButton(
            onPressed: loading ? null : onParse,
            child: loading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text(
                    'AI로 고르기',
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
          ),
        ],
      ),
    );
  }
}
