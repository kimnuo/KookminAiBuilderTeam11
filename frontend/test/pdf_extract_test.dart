import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:pdfrx/pdfrx.dart';

import 'package:kmu_notice/features/profile/pdf_text_extractor.dart';
import 'package:kmu_notice/features/profile/pii_masker.dart';

// 가상 인물 정보로 만든 한 쪽짜리 PDF.
Uint8List buildPdf(List<String> lines) {
  final content = StringBuffer('BT /F1 12 Tf 50 750 Td 16 TL\n');
  for (final l in lines) {
    content.write('($l) Tj T*\n');
  }
  content.write('ET');
  final stream = content.toString();
  final objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
        '/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>',
    '<< /Length ${stream.length} >>\nstream\n$stream\nendstream',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
  ];
  final out = StringBuffer('%PDF-1.4\n');
  final offsets = <int>[];
  for (var i = 0; i < objects.length; i++) {
    offsets.add(out.length);
    out.write('${i + 1} 0 obj\n${objects[i]}\nendobj\n');
  }
  final xref = out.length;
  out.write('xref\n0 ${objects.length + 1}\n0000000000 65535 f \n');
  for (final o in offsets) {
    out.write('${o.toString().padLeft(10, '0')} 00000 n \n');
  }
  out.write('trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\n'
      'startxref\n$xref\n%%EOF');
  return Uint8List.fromList(ascii.encode(out.toString()));
}

void main() {
  test('PDF에서 글자를 뽑고 개인정보를 가린다', () async {
    TestWidgetsFlutterBinding.ensureInitialized();
    Pdfrx.cacheDirectoryPath = Directory.systemTemp.path;
    final pdf = buildPdf([
      'Portfolio - Demo Person',
      'Phone 010-1234-5678',
      'Email demo.person@example.com',
      'Student ID 20231234',
      'Project: Campus Lost and Found App',
    ]);

    final text = await PdfTextExtractor.extract(pdf);
    expect(text, contains('Campus Lost and Found App'));

    final masked = PiiMasker.mask(text);
    expect(masked.text, isNot(contains('010-1234-5678')));
    expect(masked.text, isNot(contains('example.com')));
    expect(masked.text, isNot(contains('20231234')));
    expect(masked.counts, {'이메일': 1, '전화번호': 1, '학번': 1});
  });
}
