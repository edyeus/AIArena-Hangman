import 'package:flutter/material.dart';
import '../models/poi_model.dart';
import '../models/requirement_model.dart';
import '../models/plan_model.dart';
import 'poi_gallery_section.dart';
import 'requirements_section.dart';
import 'trip_options_section.dart';
import 'map_section.dart';

class MainViewPanel extends StatelessWidget {
  final List<POI> pois;
  final List<Requirement> requirements;
  final List<PlanOption> planOptions;
  final int selectedOptionIndex;
  final ValueChanged<int>? onOptionSelected;

  const MainViewPanel({
    super.key,
    required this.pois,
    required this.requirements,
    required this.planOptions,
    this.selectedOptionIndex = 0,
    this.onOptionSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      color: Theme.of(context).colorScheme.surface,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Trip Planner',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 12),
          Text(
            'Build your itinerary, compare routes, and pin must-see spots.',
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          const SizedBox(height: 24),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // POI Gallery — large section
                  PoiGallerySection(pois: pois),
                  const SizedBox(height: 16),
                  // Requirements
                  RequirementsSection(requirements: requirements),
                  const SizedBox(height: 16),
                  // Trip Options
                  TripOptionsSection(
                    planOptions: planOptions,
                    selectedOptionIndex: selectedOptionIndex,
                    onOptionSelected: onOptionSelected,
                  ),
                  const SizedBox(height: 16),
                  // Map
                  MapSection(
                    pois: pois,
                    planOptions: planOptions,
                    selectedOptionIndex: selectedOptionIndex,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
