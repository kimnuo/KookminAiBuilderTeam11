import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';

import 'poster_image.dart';

class PosterDialog extends StatelessWidget {
  const PosterDialog({super.key, required this.poster});
  final Map<String, dynamic> poster;
  @override
  Widget build(BuildContext context) => Dialog(
    clipBehavior: Clip.antiAlias,
    child: SizedBox(
      width: FeedConfig.posterDialogWidth,
      height: MediaQuery.sizeOf(context).height * FeedConfig.posterDialogRatio,
      child: Column(
        children: [
          Align(
            alignment: Alignment.centerRight,
            child: IconButton(
              tooltip: '포스터 닫기',
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.close_rounded),
            ),
          ),
          Expanded(
            child: InteractiveViewer(child: PosterImage(poster: poster)),
          ),
        ],
      ),
    ),
  );
}
