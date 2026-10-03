import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/notice.dart';

import 'poster_preview.dart';
import 'attachment_tile.dart';

class NoticeMedia extends StatelessWidget {
  const NoticeMedia({super.key, required this.notice});
  final Notice notice;
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final poster in notice.posters) ...[
          PosterPreview(poster: poster),
          const SizedBox(height: 18),
        ],
        if (notice.attachments.isNotEmpty) ...[
          const Text(
            '첨부파일',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 10),
          ...notice.attachments.map((file) => AttachmentTile(file: file)),
        ],
      ],
    );
  }
}
