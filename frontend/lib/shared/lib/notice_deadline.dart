import 'feed_config.dart';
import 'notice.dart';

DateTime koreaToday([DateTime? now]) {
  final kst = (now ?? DateTime.now()).toUtc().add(FeedConfig.koreaOffset);
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

bool deadlineExpired(Notice notice, {DateTime? now}) {
  final d = validDeadline(notice);
  if (d == null) return false;
  if (d['time'] == null) {
    return DateTime.parse('${d['date']}T00:00:00Z').isBefore(koreaToday(now));
  }
  return !DateTime.parse('${d['date']}T${d['time']}:00+09:00')
      .isAfter(now ?? DateTime.now());
}

String deadlineLabel(Notice notice, {DateTime? now}) {
  final clock = now ?? DateTime.now();
  final d = validDeadline(notice);
  if (d == null) return '원문 확인';
  if (deadlineExpired(notice, now: clock)) return '마감';
  final days = DateTime.parse('${d['date']}T00:00:00Z')
      .difference(koreaToday(clock))
      .inDays;
  if (days == 0) return '오늘 마감';
  return 'D-$days';
}

int compareDeadline(Notice a, Notice b, {DateTime? now}) {
  final clock = now ?? DateTime.now();
  final expired = (deadlineExpired(a, now: clock) ? 1 : 0).compareTo(
    deadlineExpired(b, now: clock) ? 1 : 0,
  );
  if (expired != 0) return expired;
  DateTime date(Notice n) {
    final d = validDeadline(n);
    return d == null
        ? DateTime.utc(9999)
        : DateTime.parse('${d['date']}T${d['time'] ?? '23:59'}:00+09:00');
  }

  final deadline = date(a).compareTo(date(b));
  if (deadline != 0) return deadline;
  final posted = b.postedAt.compareTo(a.postedAt);
  return posted != 0 ? posted : a.id.compareTo(b.id);
}
