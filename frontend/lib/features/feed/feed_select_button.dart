import 'package:flutter/material.dart';
import 'package:kmu_notice/shared/ui/app_colors.dart';

class FeedSelectButton extends StatelessWidget {
  const FeedSelectButton({
    super.key,
    required this.value,
    required this.options,
    required this.icon,
    required this.onChanged,
    required this.tooltip,
    this.compact = false,
  });
  final String value, tooltip;
  final Map<String, String> options;
  final IconData icon;
  final ValueChanged<String> onChanged;
  final bool compact;
  @override
  Widget build(BuildContext context) => PopupMenuButton<String>(
    tooltip: tooltip,
    initialValue: value,
    onSelected: onChanged,
    position: PopupMenuPosition.under,
    offset: const Offset(0, 8),
    color: Colors.white,
    surfaceTintColor: Colors.transparent,
    elevation: 8,
    constraints: const BoxConstraints(minWidth: 210, maxWidth: 300),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
    itemBuilder: (_) => options.entries.map(_option).toList(),
    child: _button(),
  );
  Widget _button() => Container(
    height: 44,
    padding: EdgeInsets.symmetric(horizontal: compact ? 10 : 14),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: const Color(0xFFE0E6ED)),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (!compact) ...[
          Icon(icon, size: 18, color: AppColors.primary),
          const SizedBox(width: 8),
        ],
        Flexible(
          child: Text(
            options[value] ?? '',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
          ),
        ),
        const SizedBox(width: 6),
        const Icon(
          Icons.keyboard_arrow_down_rounded,
          size: 18,
          color: AppColors.grey500,
        ),
      ],
    ),
  );
  PopupMenuEntry<String> _option(
    MapEntry<String, String> option,
  ) => PopupMenuItem(
    value: option.key,
    child: Row(
      children: [
        if (option.value.contains('사업단')) ...[
          const Icon(Icons.school_rounded, size: 18, color: AppColors.primary),
          const SizedBox(width: 8),
        ],
        Expanded(
          child: Text(
            option.value,
            style: TextStyle(
              fontSize: 14,
              color: option.key == value
                  ? AppColors.primary
                  : AppColors.grey700,
              fontWeight: option.key == value
                  ? FontWeight.w600
                  : FontWeight.w400,
            ),
          ),
        ),
        if (option.key == value)
          const Icon(Icons.check_rounded, size: 18, color: AppColors.primary),
      ],
    ),
  );
}
