import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice_search.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/fit_line.dart';

import 'detail_section.dart';
import 'notice_media.dart';
import 'notice_ai_sections.dart';

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
      LayoutBuilder(builder: (_, size) => _body(size.maxWidth)),
    ],
  );

  Widget _body(double width) {
    final hasMedia = notice.posters.isNotEmpty || notice.attachments.isNotEmpty;
    final sections = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: _sections(),
    );
    if (!hasMedia) return sections;
    if (width >= 620) {
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: sections),
          const SizedBox(width: 24),
          SizedBox(
            width: FeedConfig.posterSidebarWidth,
            child: NoticeMedia(notice: notice),
          ),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ConstrainedBox(
          constraints: const BoxConstraints(
            maxWidth: FeedConfig.posterStackWidth,
          ),
          child: NoticeMedia(notice: notice),
        ),
        const SizedBox(height: 24),
        sections,
      ],
    );
  }

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
    return [FitCard(notice: notice), NoticeAiSections(notice: notice), preparation];
  }
}
