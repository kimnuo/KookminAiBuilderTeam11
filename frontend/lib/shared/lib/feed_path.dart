import 'feed_config.dart';
import 'routes.dart';

// 피드로 보낼 때는 이 경로를 쓴다. FeedConfig.demo 는 주소창(Uri.base)에서 읽으므로,
// 그냥 Routes.feed 로 가면 ?demo=1 이 떨어져 나가고 데모 모드가 꺼진다.
String get feedPath => '${Routes.feed}${FeedConfig.demo ? '?demo=1' : ''}';
