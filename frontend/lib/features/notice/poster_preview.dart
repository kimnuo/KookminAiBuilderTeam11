import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';

import 'poster_dialog.dart';
import 'poster_image.dart';

class PosterPreview extends StatelessWidget {
  const PosterPreview({super.key, required this.poster});
  final Map<String, dynamic> poster;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: ConstrainedBox(
          constraints: const BoxConstraints(
            maxHeight: FeedConfig.posterPreviewHeight,
          ),
          child: PosterImage(poster: poster),
        ),
      ),
      TextButton.icon(
        onPressed: () => _zoom(context),
        icon: const Icon(Icons.zoom_in_rounded, size: 18),
        label: const Text('포스터 확대'),
      ),
    ],
  );
  void _zoom(BuildContext context) => showDialog<void>(
    context: context,
    builder: (_) => PosterDialog(poster: poster),
  );
}
