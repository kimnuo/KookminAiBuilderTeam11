import 'package:flutter/material.dart';

class PosterPreview extends StatelessWidget {
  const PosterPreview({super.key, required this.asset, required this.label});
  final String asset, label;
  @override
  Widget build(BuildContext context) => InkWell(
    onTap: () => _zoom(context),
    borderRadius: BorderRadius.circular(12),
    child: ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: Image.asset(
        asset,
        fit: BoxFit.contain,
        semanticLabel: label,
        errorBuilder: (_, _, _) => const Padding(
          padding: EdgeInsets.all(16),
          child: Text('포스터를 불러올 수 없어요.'),
        ),
      ),
    ),
  );
  void _zoom(BuildContext context) => showDialog<void>(
    context: context,
    builder: (context) => Dialog(
      clipBehavior: Clip.antiAlias,
      child: SizedBox(
        width: 650,
        height: MediaQuery.sizeOf(context).height * .86,
        child: Column(
          children: [
            Align(
              alignment: Alignment.centerRight,
              child: IconButton(
                tooltip: '닫기',
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.close_rounded),
              ),
            ),
            Expanded(
              child: InteractiveViewer(
                child: Image.asset(
                  asset,
                  semanticLabel: label,
                  fit: BoxFit.contain,
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}
