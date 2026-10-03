import 'dart:typed_data';

import 'package:pdfrx/pdfrx.dart';

// PDF 원본은 이 기기 안에서만 읽고 어디에도 저장하지 않는다.
class PdfTextExtractor {
  static Future<String> extract(Uint8List bytes) async {
    await pdfrxFlutterInitialize();
    final doc = await PdfDocument.openData(bytes);
    try {
      final buffer = StringBuffer();
      for (final page in doc.pages) {
        final text = await page.loadText();
        if (text != null) buffer.writeln(text.fullText);
      }
      return buffer.toString().trim();
    } finally {
      await doc.dispose();
    }
  }
}
