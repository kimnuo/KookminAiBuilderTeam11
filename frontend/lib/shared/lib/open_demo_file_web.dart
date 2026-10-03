import 'dart:js_interop';

import 'package:flutter/services.dart';
import 'package:web/web.dart' as web;

Future<bool> downloadDemoFile(String asset, String name) async {
  if (!asset.startsWith('assets/demo/media/') || !asset.endsWith('.pdf')) {
    return false;
  }
  try {
    final data = await rootBundle.load(asset);
    final bytes = data.buffer.asUint8List(
      data.offsetInBytes,
      data.lengthInBytes,
    );
    final blob = web.Blob(
      [bytes.toJS].toJS,
      web.BlobPropertyBag(type: 'application/pdf'),
    );
    final url = web.URL.createObjectURL(blob);
    final anchor = web.HTMLAnchorElement()
      ..href = url
      ..download = name;
    web.document.body?.append(anchor);
    anchor.click();
    anchor.remove();
    Future.delayed(
      const Duration(seconds: 30),
      () => web.URL.revokeObjectURL(url),
    );
    return true;
  } catch (_) {
    return false;
  }
}
