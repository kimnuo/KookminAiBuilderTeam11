import 'package:flutter/material.dart';

class PosterImage extends StatelessWidget {
  const PosterImage({super.key, required this.poster});
  final Map<String, dynamic> poster;
  @override
  Widget build(BuildContext context) {
    final label = poster['alt']?.toString() ?? '공고 포스터';
    if (poster['asset'] is String) {
      return Image.asset(
        poster['asset'],
        fit: BoxFit.contain,
        semanticLabel: label,
        errorBuilder: _error,
      );
    }
    return Image.network(
      poster['url'],
      fit: BoxFit.contain,
      semanticLabel: label,
      errorBuilder: _error,
      webHtmlElementStrategy: WebHtmlElementStrategy.fallback,
    );
  }

  Widget _error(BuildContext context, Object error, StackTrace? stack) =>
      const Padding(
        padding: EdgeInsets.all(16),
        child: Text('포스터를 불러올 수 없어요. 첨부파일이나 원문에서 확인해 주세요.'),
      );
}
