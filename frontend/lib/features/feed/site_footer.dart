import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

// 피드 맨 아래 바닥글. 출처는 받은 공지에서 뽑아서, 새 출처가 생기면 저절로 붙는다.
class SiteFooter extends StatelessWidget {
  const SiteFooter({super.key, required this.notices, required this.compact});
  final List<Notice> notices;
  final bool compact;

  static const _rights =
      '공지의 저작권은 각 출처에 있으며, 크노는 AI 요약과 원문 링크를 제공합니다. '
      'AI 요약은 틀릴 수 있으니 마감과 신청 방법은 원문에서 확인해 주세요.';
  static const _copyright = '© 2026 귀찮음 주식회사 · 크노 | 국민대 K-Builder 팀 11';

  @override
  Widget build(BuildContext context) {
    final sources = sourceLabels(notices);
    final style = TextStyle(
      fontSize: compact ? 12 : 13,
      height: 1.45,
      color: AppColors.grey700,
    );
    // 카테고리 칸이 남은 화면 높이에 맞춰지므로 바닥글 높이를 묶어 둔다.
    // 좁은 화면에서 글이 넘치면 이 안에서만 스크롤한다.
    return ConstrainedBox(
      constraints: BoxConstraints(maxHeight: compact ? 64 : 84),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (sources.isNotEmpty)
              Text('공지 출처: ${sources.join(' · ')}', style: style),
            Text(_rights, style: style),
            Text(_copyright, style: style.copyWith(color: AppColors.grey500)),
          ],
        ),
      ),
    );
  }
}

// 출처 이름 앞에 소속(group)이 있으면 붙인다. 예: 「국민대 본부 학사공지」
List<String> sourceLabels(Iterable<Notice> notices) {
  final labels = <String>{};
  for (final n in notices) {
    final name = n.source['name']?.toString() ?? '';
    if (name.isEmpty) continue;
    final group = n.source['group']?.toString() ?? '';
    labels.add(group.isEmpty ? name : '$group $name');
  }
  return labels.toList()..sort();
}
