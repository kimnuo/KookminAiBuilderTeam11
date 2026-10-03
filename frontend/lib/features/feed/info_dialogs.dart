import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

import 'site_footer.dart';

// 「추천 방식」 문구. 백엔드 feed/router.py·feed/service.py·core/ordering.py·
// ai/enrich.py 의 실제 동작을 옮긴 것이다. 백엔드가 바뀌면 같이 고친다.
const _recommendLines = [
  '로그인 전에는 새 글부터 보여 드려요.',
  '로그인하고 학과·학년·관심 분야·태그를 저장하면, AI가 공지마다 될 가능성과 이유 한 줄을 매겨요.',
  '추천 순: 마감 안 지난 글 → 올해 글 → AI 추천도 높은 순 → 최신 순. 지난 마감은 빠져요.',
  '거르고 줄 세우는 건 코드가, 공지를 읽고 해석하는 건 AI가 해요.',
  '마감일은 근거 문장이 원문에 그대로 있을 때만 보여요. 아니면 「원문 확인」이에요.',
  '신청 전에는 원문에서 마감과 방법을 꼭 확인해 주세요.',
];

const _sourceLines = [
  '${FeedConfig.collectMinutes}분마다 새 글을 확인해요.',
  '원문 링크로 안내해요.',
  '공지 저작권은 각 출처에 있어요.',
];

Future<void> showRecommendInfo(BuildContext context) => showDialog<void>(
  context: context,
  builder: (_) => _InfoDialog(
    title: '추천 방식',
    children: [for (final line in _recommendLines) _line(line)],
  ),
);

Future<void> showSourceInfo(BuildContext context, List<Notice> notices) {
  // 출처는 받은 공지에서 뽑는다. 바닥글과 같은 함수라 소속(group)이 있으면 앞에 붙는다.
  final sources = sourceLabels(notices);
  return showDialog<void>(
    context: context,
    builder: (_) => _InfoDialog(
      title: '수집 출처',
      children: [
        _label('지금 받아 오는 곳'),
        if (sources.isEmpty) _line('공지를 불러오면 출처가 여기 나와요.'),
        for (final s in sources) _line(s, icon: Icons.school_rounded),
        const SizedBox(height: 8),
        for (final line in _sourceLines) _line(line),
      ],
    ),
  );
}

Widget _label(String text) => Padding(
  padding: const EdgeInsets.only(bottom: 8),
  child: Text(
    text,
    style: const TextStyle(
      fontSize: 13,
      fontWeight: FontWeight.w600,
      color: AppColors.grey500,
    ),
  ),
);

Widget _line(String text, {IconData icon = Icons.check_rounded}) => Padding(
  padding: const EdgeInsets.only(bottom: 10),
  child: Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Padding(
        padding: const EdgeInsets.only(top: 3),
        child: Icon(icon, size: 18, color: AppColors.primary),
      ),
      const SizedBox(width: 10),
      Expanded(
        child: Text(
          text,
          style: const TextStyle(
            fontSize: 15,
            height: 1.5,
            color: AppColors.grey900,
          ),
        ),
      ),
    ],
  ),
);

class _InfoDialog extends StatelessWidget {
  const _InfoDialog({required this.title, required this.children});
  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Dialog(
    insetPadding: const EdgeInsets.all(16),
    child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 560),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(24, 12, 12, 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _header(context),
            const SizedBox(height: 8),
            Flexible(
              child: SingleChildScrollView(
                padding: const EdgeInsets.only(right: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: children,
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );

  Widget _header(BuildContext context) => Row(
    children: [
      Expanded(
        child: Text(
          title,
          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
        ),
      ),
      IconButton(
        tooltip: '닫기',
        onPressed: () => Navigator.pop(context),
        icon: const Icon(Icons.close_rounded),
      ),
    ],
  );
}
