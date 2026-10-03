import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:kmu_notice/features/notice/notice_page.dart';
import 'package:kmu_notice/features/apply_helper/apply_panel.dart';
import 'package:kmu_notice/shared/lib/feed_config.dart';
import 'package:kmu_notice/shared/lib/routes.dart';

Future<void> openNoticeDialog(BuildContext context, String id) =>
    showDialog<void>(
      context: context,
      builder: (dialogContext) =>
          NoticeDialog(id: id, onEdit: () => _edit(context, dialogContext, id)),
    );

Future<void> _edit(
  BuildContext pageContext,
  BuildContext dialogContext,
  String id,
) async {
  Navigator.of(dialogContext).pop();
  await pageContext.push(Routes.applicantInfo);
  if (pageContext.mounted) await openNoticeDialog(pageContext, id);
}

class NoticeDialog extends StatelessWidget {
  const NoticeDialog({super.key, required this.id, required this.onEdit});
  final String id;
  final Future<void> Function() onEdit;
  @override
  Widget build(BuildContext context) => Dialog(
    insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
    clipBehavior: Clip.antiAlias,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
    child: SizedBox(
      width: FeedConfig.detailDialogWidth,
      height: math.min(
        FeedConfig.detailDialogHeight,
        MediaQuery.sizeOf(context).height * FeedConfig.detailDialogRatio,
      ),
      child: NoticePage(
        id: id,
        onClose: () => Navigator.of(context).pop(),
        preparation: (notice) => ApplyPanel(notice: notice, onEdit: onEdit),
      ),
    ),
  );
}
