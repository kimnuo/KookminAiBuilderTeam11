import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:kmu_notice/shared/api/api_client.dart';
import 'package:kmu_notice/shared/api/auth_api.dart';
import 'package:kmu_notice/shared/lib/routes.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';
import 'package:kmu_notice/shared/ui/app_text_field.dart';
import 'package:kmu_notice/shared/ui/step_scaffold.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _nickname = TextEditingController();
  final _password = TextEditingController();
  bool _loading = false;
  String? _error;

  bool get _valid => _nickname.text.isNotEmpty && _password.text.isNotEmpty;

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await AuthApi.login(_nickname.text.trim(), _password.text);
      if (mounted) context.go(Routes.feed);
    } on ApiException catch (e) {
      setState(() => _error = e.statusCode == 401
          ? '닉네임 또는 비밀번호가 맞지 않아요.'
          : '로그인하지 못했어요. 잠시 후 다시 시도해 주세요.');
    } catch (_) {
      setState(() => _error = '서버에 연결하지 못했어요.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return StepScaffold(
      title: '다시 오셨네요',
      ctaLabel: '로그인',
      ctaLoading: _loading,
      onCta: _valid ? _submit : null,
      children: [
        AppTextField(
          label: '닉네임',
          controller: _nickname,
          onChanged: (_) => setState(() {}),
        ),
        AppTextField(
          label: '비밀번호',
          controller: _password,
          obscure: true,
          errorText: _error,
          onChanged: (_) => setState(() {}),
        ),
        Center(
          child: TextButton(
            onPressed: () => context.pushReplacement(Routes.signup),
            child: const Text(
              '처음이에요, 가입할게요',
              style: TextStyle(color: AppColors.grey500),
            ),
          ),
        ),
      ],
    );
  }
}
