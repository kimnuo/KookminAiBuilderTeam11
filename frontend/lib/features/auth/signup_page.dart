import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/api_client.dart';
import 'package:kmu_notice/shared/api/auth_api.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/app_text_field.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';
import 'password_rule_hints.dart';
import 'signup_rules.dart';

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final _nickname = TextEditingController();
  final _password = TextEditingController();
  bool _loading = false;
  String? _nicknameError;
  String? _formError;

  bool get _valid =>
      SignupRules.nicknameLength(_nickname.text) &&
      SignupRules.passwordValid(_password.text);

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _nicknameError = null;
      _formError = null;
    });
    try {
      await AuthApi.signup(_nickname.text.trim(), _password.text);
      if (mounted) context.go(Routes.consent);
    } on ApiException catch (e) {
      setState(() => e.statusCode == 409
          ? _nicknameError = '이미 사용 중인 닉네임이에요.'
          : _formError = '가입하지 못했어요. 잠시 후 다시 시도해 주세요.');
    } catch (_) {
      setState(() => _formError = '서버에 연결하지 못했어요.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _onNicknameChanged(String _) => setState(() => _nicknameError = null);

  @override
  Widget build(BuildContext context) {
    return StepScaffold(
      title: '닉네임과 비밀번호를\n만들어 주세요',
      subtitle: '실명 대신 닉네임을 써 주세요.',
      ctaLabel: '가입하기',
      ctaLoading: _loading,
      onCta: _valid ? _submit : null,
      children: [
        AppTextField(
          label: '닉네임',
          controller: _nickname,
          hint: '${SignupRules.nicknameMin}~${SignupRules.nicknameMax}자',
          errorText: _nicknameError,
          onChanged: _onNicknameChanged,
        ),
        AppTextField(
          label: '비밀번호',
          controller: _password,
          hint: '영문과 숫자를 섞어 ${SignupRules.passwordMin}자 이상',
          obscure: true,
          onChanged: (_) => setState(() {}),
          footer: PasswordRuleHints(password: _password.text),
        ),
        if (_formError != null)
          Text(_formError!, style: const TextStyle(color: AppColors.danger)),
        const Text(
          '비밀번호 찾기 기능이 없어요. 잊지 않도록 주의해 주세요.',
          style: TextStyle(fontSize: 13, color: AppColors.grey500),
        ),
      ],
    );
  }
}
