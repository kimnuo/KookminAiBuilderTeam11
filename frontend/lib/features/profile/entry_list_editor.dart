import 'package:flutter/material.dart';

import 'package:kmu_notice/shared/ui/app_colors.dart';

class EntryListEditor extends StatefulWidget {
  const EntryListEditor({
    super.key,
    required this.label,
    required this.hint,
    required this.items,
    required this.onChanged,
  });

  final String label;
  final String hint;
  final List<String> items;
  final ValueChanged<List<String>> onChanged;

  @override
  State<EntryListEditor> createState() => _EntryListEditorState();
}

class _EntryListEditorState extends State<EntryListEditor> {
  final _input = TextEditingController();

  void _add() {
    final v = _input.text.trim();
    if (v.isEmpty) return;
    widget.onChanged([...widget.items, v]);
    _input.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.label,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: AppColors.grey700,
            ),
          ),
          const SizedBox(height: 8),
          for (final item in widget.items) _row(item),
          _inputRow(),
        ],
      ),
    );
  }

  Widget _row(String item) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Expanded(child: Text(item, style: const TextStyle(fontSize: 16))),
          GestureDetector(
            onTap: () => widget.onChanged(
              widget.items.where((e) => e != item).toList(),
            ),
            child: const Icon(Icons.close, size: 18, color: AppColors.grey500),
          ),
        ],
      ),
    );
  }

  Widget _inputRow() {
    return Container(
      margin: const EdgeInsets.only(top: 4),
      padding: const EdgeInsets.only(left: 16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _input,
              onSubmitted: (_) => _add(),
              decoration: InputDecoration(
                hintText: widget.hint,
                hintStyle: const TextStyle(color: AppColors.grey500),
                border: InputBorder.none,
              ),
            ),
          ),
          IconButton(
            onPressed: _add,
            icon: const Icon(Icons.add_circle, color: AppColors.primary),
          ),
        ],
      ),
    );
  }
}
