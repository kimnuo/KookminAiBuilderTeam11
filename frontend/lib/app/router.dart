import 'package:go_router/go_router.dart';

import 'package:kmu_notice/features/auth/consent_page.dart';
import 'package:kmu_notice/features/auth/login_page.dart';
import 'package:kmu_notice/features/auth/signup_page.dart';
import 'package:kmu_notice/features/auth/welcome_page.dart';
import 'package:kmu_notice/features/onboarding/interests_page.dart';
import 'package:kmu_notice/features/onboarding/major_year_page.dart';
import 'package:kmu_notice/features/profile/applicant_info_page.dart';
import 'package:kmu_notice/features/profile/history_page.dart';
import 'package:kmu_notice/features/profile/portfolio_page.dart';
import 'package:kmu_notice/features/profile/portfolio_review_page.dart';
import 'package:kmu_notice/features/profile/profile_analysis.dart';
import 'package:kmu_notice/features/profile/settings_page.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'feed_placeholder_page.dart';

final appRouter = GoRouter(
  initialLocation: Routes.welcome,
  routes: [
    GoRoute(path: Routes.welcome, builder: (_, _) => const WelcomePage()),
    GoRoute(path: Routes.signup, builder: (_, _) => const SignupPage()),
    GoRoute(path: Routes.login, builder: (_, _) => const LoginPage()),
    GoRoute(path: Routes.consent, builder: (_, _) => const ConsentPage()),
    GoRoute(
      path: Routes.onboardingMajor,
      builder: (_, _) => const MajorYearPage(),
    ),
    GoRoute(
      path: Routes.onboardingInterests,
      builder: (_, _) => const InterestsPage(),
    ),
    GoRoute(
      path: Routes.profileHistory,
      builder: (_, _) => const HistoryPage(),
    ),
    GoRoute(path: Routes.portfolio, builder: (_, _) => const PortfolioPage()),
    GoRoute(
      path: Routes.portfolioReview,
      builder: (_, state) =>
          PortfolioReviewPage(analysis: state.extra! as ProfileAnalysis),
    ),
    GoRoute(
      path: Routes.applicantInfo,
      builder: (_, _) => const ApplicantInfoPage(),
    ),
    GoRoute(path: Routes.settings, builder: (_, _) => const SettingsPage()),
    GoRoute(
      path: Routes.feed,
      builder: (_, _) => const FeedPlaceholderPage(),
    ),
  ],
);
