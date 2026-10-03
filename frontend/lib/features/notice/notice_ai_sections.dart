import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';

import 'detail_section.dart';
import 'digest_sections.dart';

class NoticeAiSections extends StatelessWidget {
  const NoticeAiSections({super.key, required this.notice});
  final Notice notice;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      DetailSection(
        title: '핵심 요약',
        lines: notice.summary.isEmpty
            ? ['요약 정보가 없어요. 원문을 확인해 주세요.']
            : notice.summary,
      ),
      _deadline(),
      if (notice.audience?.trim().isNotEmpty ?? false)
        DetailSection(title: '신청 대상', lines: [notice.audience!]),
      if (notice.apply?.trim().isNotEmpty ?? false)
        DetailSection(title: '신청 방법', lines: [notice.apply!]),
      DigestSections(notice: notice),
      if (notice.reasons.isNotEmpty)
        DetailSection(title: '추천 이유', lines: notice.reasons),
    ],
  );

  Widget _deadline() {
    final d = validDeadline(notice);
    return DetailSection(
      title: '마감일 · ${deadlineLabel(notice)}',
      lines: d == null
          ? ['근거가 있는 마감일 정보가 없어요. 원문을 확인해 주세요.']
          : [
              '${d['date']}${d['time'] == null ? '' : ' ${d['time']}'} (한국 시간)',
              '근거: ${d['evidence']}',
            ],
    );
  }
}
