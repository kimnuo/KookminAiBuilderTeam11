import 'package:flutter/foundation.dart';

import 'package:kmu_notice/shared/api/notice_api.dart';
import 'package:kmu_notice/shared/lib/interest_groups.dart';
import 'package:kmu_notice/shared/lib/interest_store.dart';
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
  bool _seeded = false;

  Future<void> load() async {
    final generation = ++_generation;
    loading = true;
    error = null;
    notifyListeners();
    try {
      await _seedSelection();
      final data = await NoticeApi.feed(sort);
      if (generation == _generation) notices = data;
    } catch (_) {
      if (generation == _generation) error = '공고를 불러오지 못했어요. 연결을 확인해 주세요.';
    }
    if (generation != _generation) return;
    loading = false;
    notifyListeners();
  }

  // 온보딩에서 고른 분야를 처음 한 번만 선택값으로 깐다. 그 뒤로는 사용자가 고른 대로 둔다.
  Future<void> _seedSelection() async {
    if (_seeded) return;
    _seeded = true;
    try {
      selected.addAll(feedGroupIdsFor(await InterestStore.load()));
    } catch (_) {
      // 저장값을 못 읽어도 피드는 그대로 연다.
    }
  }

  List<Notice> get visible {
    final result = notices
        .where(
          (n) =>
              matchesSearch(n, query) &&
              (source.isEmpty || n.sourceId == source) &&
              (sort != 'recommend' || !deadlineExpired(n)),
        )
        .toList();
    if (sort == 'deadline') result.sort(compareDeadline);
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
