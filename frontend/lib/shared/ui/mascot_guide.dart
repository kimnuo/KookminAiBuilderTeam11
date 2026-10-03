import 'package:flutter/material.dart';

import 'app_colors.dart';

enum KnoMood { normal, alert, reading }

// 크노가 말풍선으로 한두 줄 안내한다. 그림은 표시 크기보다 큰 PNG를 줄여 쓴다.
class MascotGuide extends StatelessWidget {
  const MascotGuide(
    this.message, {
    super.key,
    this.mood = KnoMood.normal,
    this.size = 56,
  });

  final String message;
  final KnoMood mood;
  final double size;

  String get _file => switch (mood) {
    KnoMood.normal => 'default',
    KnoMood.alert => 'alert',
    KnoMood.reading => 'reading',
  };

  @override
  Widget build(BuildContext context) {
    final px = size <= 48 ? 128 : 512;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Image.asset(
          'assets/mascot/mascot-$_file-$px.png',
          width: size,
          height: size,
          filterQuality: FilterQuality.medium,
          semanticLabel: '크노',
        ),
        const SizedBox(width: 8),
        Flexible(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: const BoxDecoration(
              color: AppColors.primaryLight,
              // 크노 쪽 아래 모서리만 덜 둥글게 해서 말꼬리처럼 보이게 한다.
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
                bottomRight: Radius.circular(16),
                bottomLeft: Radius.circular(4),
              ),
            ),
            child: Text(
              message,
              style: const TextStyle(
                fontSize: 14,
                height: 1.45,
                color: AppColors.grey900,
              ),
            ),
          ),
        ),
      ],
    );
  }
}
