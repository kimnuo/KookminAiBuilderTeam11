import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

// PRD 10절 Profile.history 형식. 이 기기에만 저장하고 서버로 보내지 않는다.
class ProfileHistory {
  ProfileHistory({
    List<String>? tags,
    List<String>? skills,
    List<Map<String, dynamic>>? projects,
    List<Map<String, dynamic>>? awards,
    List<Map<String, dynamic>>? activities,
  })  : tags = tags ?? [],
        skills = skills ?? [],
        projects = projects ?? [],
        awards = awards ?? [],
        activities = activities ?? [];

  final List<String> tags;
  final List<String> skills;
  final List<Map<String, dynamic>> projects;
  final List<Map<String, dynamic>> awards;
  final List<Map<String, dynamic>> activities;

  Map<String, dynamic> toJson() => {
        'tags': tags,
        'skills': skills,
        'projects': projects,
        'awards': awards,
        'activities': activities,
      };

  static List<Map<String, dynamic>> _maps(dynamic v) =>
      List<Map<String, dynamic>>.from(
        (v as List? ?? const []).map((e) => Map<String, dynamic>.from(e)),
      );

  factory ProfileHistory.fromJson(Map<String, dynamic> j) => ProfileHistory(
        tags: List<String>.from(j['tags'] ?? const []),
        skills: List<String>.from(j['skills'] ?? const []),
        projects: _maps(j['projects']),
        awards: _maps(j['awards']),
        activities: _maps(j['activities']),
      );
}

class ProfileStore {
  static const _key = 'profile.history';

  static Future<ProfileHistory> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null) return ProfileHistory();
    return ProfileHistory.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }

  static Future<void> save(ProfileHistory h) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, jsonEncode(h.toJson()));
  }
}
