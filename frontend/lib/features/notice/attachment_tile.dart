import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/lib/open_demo_file.dart';
import 'package:kmu_notice/shared/lib/open_original.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

class AttachmentTile extends StatelessWidget {
  const AttachmentTile({super.key, required this.file});
  final Map<String, dynamic> file;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(12),
      child: ListTile(
        dense: true,
        contentPadding: const EdgeInsets.symmetric(horizontal: 10),
        leading: const Icon(
          Icons.description_outlined,
          color: AppColors.primary,
          size: 22,
        ),
        title: Text(
          file['name']?.toString() ?? '첨부파일',
          maxLines: 2,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          file['asset'] != null ? 'PDF 다운로드' : '파일 열기',
          style: const TextStyle(fontSize: 11, color: AppColors.grey500),
        ),
        trailing: const Icon(Icons.download_rounded, size: 18),
        onTap: () => _open(context),
      ),
    ),
  );
  Future<void> _open(BuildContext context) async {
    final opened = file['asset'] is String
        ? await downloadDemoFile(
            file['asset'],
            file['name']?.toString() ?? 'attachment.pdf',
          )
        : await openOriginal(file['url']?.toString() ?? '');
    if (!opened && context.mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('첨부파일을 열 수 없어요.')));
    }
  }
}
