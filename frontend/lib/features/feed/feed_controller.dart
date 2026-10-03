import 'package:flutter/foundation.dart';

import 'package:kmu_notice/shared/api/notice_api.dart';
import 'package:kmu_notice/shared/lib/notice.dart';
import 'package:kmu_notice/shared/lib/notice_search.dart';
import 'package:kmu_notice/shared/lib/notice_deadline.dart';

class FeedController extends ChangeNotifier {
  List<Notice> notices = [];
  final Set<String> selected = {};
  String query = '', source = '', sort = 'recommend';
  String? error;
  bool loading = true;
  int _generation = 0;

  Future<void> load() async {
    final generation = ++_generation;
    loading = true;
    error = null;
    notifyListeners();
    try {
      final data = await NoticeApi.feed(sort);
      if (generation == _generation) notices = data;
    } catch (_) {
      if (generation == _generation) error = '공고를 불러오지 못했어요. 연결을 확인해 주세요.';
    }
    if (generation != _generation) return;
    loading = false;
    notifyListeners();
  }

  List<Notice> get visible {
    final now = DateTime.now();
    final result = notices
        .where(
          (n) =>
              matchesSearch(n, query) &&
              (source.isEmpty || n.sourceId == source) &&
              (sort != 'recommend' || !deadlineExpired(n, now: now)),
        )
        .toList();
    if (sort == 'deadline') {
      result.sort((a, b) => compareDeadline(a, b, now: now));
    }
    return result;
  }

  List<Notice> get chosen => visible
      .where(
        (n) =>
            selected.isEmpty ||
            groupsFor(n).any((g) => selected.contains(g.id)),
      )
      .toList();
  Map<String, String> get sources => {
    for (final n in notices) n.sourceId: n.sourceName,
  };
  void setQuery(String value) {
    query = value;
    notifyListeners();
  }

  void setSource(String value) {
    source = value;
    notifyListeners();
  }

  void setSort(String value) {
    sort = value;
    load();
  }

  void toggle(String id) {
    if (!selected.add(id)) selected.remove(id);
    notifyListeners();
  }

  void clearSelection() {
    selected.clear();
    notifyListeners();
  }

  void resetHome() {
    query = '';
    source = '';
    selected.clear();
    final reload = sort != 'recommend';
    sort = 'recommend';
    if (reload) {
      load();
    } else {
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _generation++;
    super.dispose();
  }
}
