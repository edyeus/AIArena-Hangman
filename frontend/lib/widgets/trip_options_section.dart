import 'package:flutter/material.dart';
import '../models/plan_model.dart';

class TripOptionsSection extends StatelessWidget {
  final List<PlanOption> planOptions;
  final int selectedOptionIndex;
  final ValueChanged<int>? onOptionSelected;
  const TripOptionsSection({
    super.key,
    required this.planOptions,
    this.selectedOptionIndex = 0,
    this.onOptionSelected,
  });

  @override
  Widget build(BuildContext context) {
    if (planOptions.isEmpty) {
      return _buildEmptyState(context);
    }

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Trip Options',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const Spacer(),
              Chip(
                label: Text('${planOptions.length} options'),
                visualDensity: VisualDensity.compact,
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 500,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: planOptions.asMap().entries.map((entry) {
                  final index = entry.key;
                  final option = entry.value;
                  return Padding(
                    padding: EdgeInsets.only(right: index < planOptions.length - 1 ? 16 : 0),
                    child: GestureDetector(
                      onTap: () => onOptionSelected?.call(index),
                      child: _buildOptionCard(context, option, index + 1, index == selectedOptionIndex),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOptionCard(BuildContext context, PlanOption option, int optionNumber, bool isSelected) {
    return Container(
      width: 320,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isSelected
              ? Theme.of(context).colorScheme.primary
              : Theme.of(context).dividerColor,
          width: isSelected ? 2 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primaryContainer,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'Option $optionNumber',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const Spacer(),
                    Text(
                      option.overallCost,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Theme.of(context).colorScheme.primary,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  option.generalNotes,
                  style: Theme.of(context).textTheme.bodyMedium,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          // Days list
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: option.days.length,
              separatorBuilder: (context, index) => const Divider(height: 24),
              itemBuilder: (context, index) {
                return _buildDayCard(context, option.days[index], index + 1);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDayCard(BuildContext context, Day day, int dayNumber) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.secondary,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'Day $dayNumber',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSecondary,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                day.highlight,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        if (day.lodging != null) ...[
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.hotel, size: 16, color: Theme.of(context).colorScheme.primary),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  day.lodging!,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        fontStyle: FontStyle.italic,
                      ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ],
        const SizedBox(height: 12),
        ...day.blocks.map((block) => _buildTimeBlock(context, block)),
      ],
    );
  }

  Widget _buildTimeBlock(BuildContext context, Block block) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            block.time,
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            block.description,
            style: Theme.of(context).textTheme.bodyMedium,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
          ),
          if (block.transportation != null) ...[
            const SizedBox(height: 6),
            Row(
              children: [
                Icon(
                  _getTransportIcon(block.transportation!.method ?? ''),
                  size: 16,
                  color: Theme.of(context).colorScheme.secondary,
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    [
                      if (block.transportation!.duration != null) block.transportation!.duration!,
                      if (block.transportation!.method != null) block.transportation!.method!,
                    ].join(' · '),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.secondary,
                        ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (block.transportation!.cost != null)
                  Text(
                    ' · \$${block.transportation!.cost!.toStringAsFixed(2)}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.secondary,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
              ],
            ),
          ],
          if (block.pois != null && block.pois!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Wrap(
              spacing: 4,
              runSpacing: 4,
              children: block.pois!.map((poi) {
                return Chip(
                  label: Text(poi.name, style: const TextStyle(fontSize: 11)),
                  avatar: Icon(_getPoiIcon(poi.poiType), size: 14),
                  visualDensity: VisualDensity.compact,
                  padding: EdgeInsets.zero,
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  IconData _getTransportIcon(String method) {
    final methodLower = method.toLowerCase();
    if (methodLower.contains('walk')) return Icons.directions_walk;
    if (methodLower.contains('subway') || methodLower.contains('metro')) return Icons.subway;
    if (methodLower.contains('bus')) return Icons.directions_bus;
    if (methodLower.contains('taxi') || methodLower.contains('car')) return Icons.directions_car;
    if (methodLower.contains('train')) return Icons.train;
    if (methodLower.contains('bike')) return Icons.directions_bike;
    if (methodLower.contains('boat') || methodLower.contains('ferry')) return Icons.directions_boat;
    return Icons.directions;
  }

  IconData _getPoiIcon(String poiType) {
    switch (poiType) {
      case 'restaurant':
        return Icons.restaurant;
      case 'lodge':
        return Icons.hotel;
      case 'tourist_destination':
        return Icons.place;
      default:
        return Icons.location_on;
    }
  }

  Widget _buildEmptyState(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.event_available, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No Trip Options Yet',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.grey[700],
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Tell the assistant your dates and preferences\nto generate personalized itineraries!',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
