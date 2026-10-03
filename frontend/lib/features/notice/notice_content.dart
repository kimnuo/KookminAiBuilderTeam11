import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';
import 'package:kmu_notice/shared/lib/notice_search.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

import 'detail_section.dart';

class NoticeContent extends StatelessWidget {
  const NoticeContent({
    super.key,
    required this.notice,
    required this.preparation,
  });
  final Notice notice;
  final Widget preparation;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        groupsFor(notice).map((g) => g.label).join(' · '),
        style: const TextStyle(
          color: AppColors.primary,
          fontWeight: FontWeight.w600,
        ),
      ),
      const SizedBox(height: 14),
      SelectableText(
        notice.title,
        style: const TextStyle(
          fontSize: 27,
          fontWeight: FontWeight.w700,
          height: 1.4,
        ),
      ),
      const SizedBox(height: 12),
      Text(
        '${notice.sourceName} · ${notice.postedAt}',
        style: const TextStyle(color: AppColors.grey500),
      ),
      const SizedBox(height: 32),
      ..._sections(),
    ],
  );

  List<Widget> _sections() {
    if (notice.ai.isEmpty) {
      return [
        DetailSection(
          title: '원문에서 확인해 주세요',
          lines: [
            notice.aiStatus == 'failed' ? 'AI 분석을 완료하지 못했어요.' : 'AI 분석 중이에요.',
          ],
        ),
      ];
    }
    final d = validDeadline(notice);
    return [
      DetailSection(
        title: '핵심 요약',
        lines: notice.summary.isEmpty
            ? ['요약 정보가 없어요. 원문을 확인해 주세요.']
            : notice.summary,
      ),
      DetailSection(
        title: '마감일 · ${deadlineLabel(notice)}',
        lines: d == null
            ? ['근거가 있는 마감일 정보가 없어요. 원문을 확인해 주세요.']
            : [
                '${d['date']}${d['time'] == null ? '' : ' ${d['time']}'} (한국 시간)',
                '근거: ${d['evidence']}',
              ],
      ),
      if (notice.audience?.trim().isNotEmpty ?? false)
        DetailSection(title: '신청 대상', lines: [notice.audience!]),
      if (notice.apply?.trim().isNotEmpty ?? false)
        DetailSection(title: '신청 방법', lines: [notice.apply!]),
      if (notice.reasons.isNotEmpty)
        DetailSection(title: '추천 이유', lines: notice.reasons),
      preparation,
    ];
  }
}
