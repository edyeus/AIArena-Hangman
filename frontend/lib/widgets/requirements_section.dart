import 'package:flutter/material.dart';
import '../models/requirement_model.dart';

class RequirementsSection extends StatelessWidget {
  final List<Requirement> requirements;
  const RequirementsSection({super.key, required this.requirements});

  @override
  Widget build(BuildContext context) {
    if (requirements.isEmpty) {
      return _buildEmptyState(context);
    }

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Requirements',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: requirements.map((req) => _buildChip(context, req)).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildChip(BuildContext context, Requirement req) {
    return Chip(
      label: Text(
        req.description,
        style: TextStyle(
          color: _getTextColor(req.priority),
          fontSize: 14,
        ),
      ),
      backgroundColor: _getBackgroundColor(req.priority),
      avatar: Icon(
        _getPriorityIcon(req.priority),
        size: 18,
        color: _getTextColor(req.priority),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
    );
  }

  Color _getBackgroundColor(Priority priority) {
    switch (priority) {
      case Priority.mustHave:
        return Colors.red.shade100;
      case Priority.avoid:
        return Colors.orange.shade100;
      case Priority.preferred:
        return Colors.blue.shade100;
    }
  }

  Color _getTextColor(Priority priority) {
    switch (priority) {
      case Priority.mustHave:
        return Colors.red.shade800;
      case Priority.avoid:
        return Colors.orange.shade800;
      case Priority.preferred:
        return Colors.blue.shade800;
    }
  }

  IconData _getPriorityIcon(Priority priority) {
    switch (priority) {
      case Priority.mustHave:
        return Icons.star;
      case Priority.avoid:
        return Icons.block;
      case Priority.preferred:
        return Icons.favorite_border;
    }
  }

  Widget _buildEmptyState(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      child: Row(
        children: [
          Icon(Icons.checklist, size: 24, color: Colors.grey[400]),
          const SizedBox(width: 12),
          Text(
            'No requirements captured yet — tell the assistant your preferences!',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
          ),
        ],
      ),
    );
  }
}
