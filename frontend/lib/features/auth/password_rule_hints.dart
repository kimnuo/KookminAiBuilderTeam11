import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'signup_rules.dart';

class PasswordRuleHints extends StatelessWidget {
  const PasswordRuleHints({super.key, required this.password});

  final String password;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Wrap(
        spacing: 16,
        children: [
          _hint('${SignupRules.passwordMin}자 이상', SignupRules.passwordLength(password)),
          _hint('영문 포함', SignupRules.hasLetter(password)),
          _hint('숫자 포함', SignupRules.hasDigit(password)),
        ],
      ),
    );
  }

  Widget _hint(String label, bool ok) {
    final color = ok ? AppColors.primary : AppColors.grey500;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.check_rounded, size: 16, color: color),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 13, color: color)),
      ],
    );
  }
}
