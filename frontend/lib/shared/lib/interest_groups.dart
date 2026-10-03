import 'catalog.dart';
import 'feed_config.dart';

// 온보딩 관심 분야(Catalog.categories)를 이름이 같은 피드 카드(noticeGroups)의 id로 옮긴다.
// 예전 이름으로 저장된 값도 서비스 분류로 바꿔서 찾는다.
Set<String> feedGroupIdsFor(Iterable<String> categories) {
  final wanted = Catalog.serviceCategories(categories);
  return {
    for (final g in noticeGroups)
      if (wanted.contains(g.label)) g.id,
  };
}
