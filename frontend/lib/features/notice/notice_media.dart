import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/notice.dart';

import 'poster_preview.dart';
import 'attachment_tile.dart';

class NoticeMedia extends StatelessWidget {
  const NoticeMedia({super.key, required this.notice});
  final Notice notice;
  @override
  Widget build(BuildContext context) {
    final poster = mapValue(notice.previewMedia['poster']);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (poster['asset'] is String) ...[
          PosterPreview(
            asset: poster['asset'],
            label: poster['alt'] ?? notice.title,
          ),
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
