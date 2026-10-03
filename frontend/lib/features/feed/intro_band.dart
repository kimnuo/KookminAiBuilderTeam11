import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

// 피드 맨 위 소개 띠. 크노가 무엇을 하는지 한 줄과 짧은 세 가지로 알린다.
// 카테고리 칸이 남은 화면 높이에 맞춰지므로 띠 높이를 maxHeight 로 묶는다.
// 좁은 화면에서 글이 넘치면 이 안에서만 스크롤한다.
class IntroBand extends StatelessWidget {
  const IntroBand({
    super.key,
    required this.compact,
    required this.maxHeight,
    required this.onClose,
  });
  final bool compact;
  final double maxHeight;
  final VoidCallback onClose;

  static const _title = '흩어진 국민대 공지를 AI가 대신 읽고, 내 분야만 골라 보여 드려요';
  static const _points = [
    (Icons.auto_awesome, 'AI 요약·마감일과 근거 문장'),
    (Icons.sync_rounded, '본부·단과대 공지를 ${FeedConfig.collectMinutes}분마다 수집'),
    (Icons.person_outline_rounded, '로그인하면 내 분야·학년에 맞춰 추천'),
  ];

  @override
  Widget build(BuildContext context) => Container(
    constraints: BoxConstraints(maxHeight: maxHeight),
    padding: EdgeInsets.fromLTRB(compact ? 12 : 18, 8, 4, 8),
    decoration: BoxDecoration(
      color: AppColors.primaryLight,
      borderRadius: BorderRadius.circular(12),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(child: SingleChildScrollView(child: _body())),
        IconButton(
          tooltip: '소개 닫기',
          iconSize: 18,
          visualDensity: VisualDensity.compact,
          onPressed: onClose,
          icon: const Icon(Icons.close_rounded, color: AppColors.grey500),
        ),
      ],
    ),
  );

  Widget _body() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        _title,
        style: TextStyle(
          fontSize: compact ? 15 : 17,
          fontWeight: FontWeight.w700,
          color: AppColors.grey900,
        ),
      ),
      const SizedBox(height: 6),
      Wrap(
        spacing: 8,
        runSpacing: 6,
        children: [for (final p in _points) _point(p.$1, p.$2)],
      ),
    ],
  );

  Widget _point(IconData icon, String label) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(999),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 15, color: AppColors.primary),
        const SizedBox(width: 5),
        Flexible(
          child: Text(
            label,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontSize: compact ? 12 : 13,
              fontWeight: FontWeight.w500,
              color: AppColors.grey700,
            ),
          ),
        ),
      ],
    ),
  );
}
