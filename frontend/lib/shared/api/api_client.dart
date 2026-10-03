import 'dart:convert';

import 'package:http/http.dart' as http;

import 'package:kmu_notice/shared/lib/app_config.dart';

class ApiException implements Exception {
  ApiException(this.statusCode, this.message);
  final int statusCode;
  final String message;

  @override
  String toString() => message;
}

class ApiClient {
  static String? token;

  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  static Future<Map<String, dynamic>> post(
    String path,
    Map<String, dynamic> body,
  ) async {
    final res = await http.post(
      Uri.parse('${AppConfig.apiBaseUrl}$path'),
      headers: _headers,
      body: jsonEncode(body),
    );
    return _decode(res);
  }

  static Future<Map<String, dynamic>> put(
    String path,
    Map<String, dynamic> body,
  ) async {
    final res = await http.put(
      Uri.parse('${AppConfig.apiBaseUrl}$path'),
      headers: _headers,
      body: jsonEncode(body),
    );
    return _decode(res);
  }

  static Future<Map<String, dynamic>> get(String path) async {
    final res = await http.get(
      Uri.parse('${AppConfig.apiBaseUrl}$path'),
      headers: _headers,
    );
    return _decode(res);
  }

  static Future<Map<String, dynamic>> delete(String path) async {
    final res = await http.delete(
      Uri.parse('${AppConfig.apiBaseUrl}$path'),
      headers: _headers,
    );
    return _decode(res);
  }

  static Map<String, dynamic> _decode(http.Response res) {
    final text = utf8.decode(res.bodyBytes);
    if (res.statusCode >= 400) {
      throw ApiException(res.statusCode, text.isEmpty ? '요청 실패' : text);
    }
    if (text.isEmpty) return {};
    return jsonDecode(text) as Map<String, dynamic>;
  }
}
