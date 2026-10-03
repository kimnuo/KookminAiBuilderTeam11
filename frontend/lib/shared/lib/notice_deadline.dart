import 'feed_config.dart';
import 'notice.dart';

DateTime koreaToday() {
  final kst = DateTime.now().toUtc().add(FeedConfig.koreaOffset);
  return DateTime.utc(kst.year, kst.month, kst.day);
}

Map<String, dynamic>? validDeadline(Notice notice) {
  final d = mapValue(notice.ai['deadline']);
  final date = d['date']?.toString() ?? '';
  if (d['evidence'] is! String || (d['evidence'] as String).trim().isEmpty) {
    return null;
  }
  if (!RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(date)) return null;
  final parsed = DateTime.tryParse(date);
  if (parsed == null || parsed.toIso8601String().substring(0, 10) != date) {
    return null;
  }
  final time = d['time'];
  if (time != null && !RegExp(r'^([01]\d|2[0-3]):[0-5]\d$').hasMatch('$time')) {
    return null;
  }
  return d;
}

bool deadlineExpired(Notice notice) {
  final d = validDeadline(notice);
  if (d == null) return false;
  if (d['time'] == null) {
    return DateTime.parse('${d['date']}T00:00:00Z').isBefore(koreaToday());
  }
  return !DateTime.parse('${d['date']}T${d['time']}:00+09:00')
      .isAfter(DateTime.now());
}

String deadlineLabel(Notice notice) {
  final d = validDeadline(notice);
  if (d == null) return '원문 확인';
  if (deadlineExpired(notice)) return '마감';
  final days = DateTime.parse('${d['date']}T00:00:00Z')
      .difference(koreaToday())
      .inDays;
  if (days == 0) return '오늘 마감';
  return 'D-$days';
}

int compareDeadline(Notice a, Notice b) {
  DateTime date(Notice n) {
    final d = validDeadline(n);
    return d == null
        ? DateTime.utc(9999)
        : DateTime.parse('${d['date']}T${d['time'] ?? '23:59'}:00+09:00');
  }

  return date(a).compareTo(date(b));
}
