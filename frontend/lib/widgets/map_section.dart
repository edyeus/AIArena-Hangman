import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/poi_model.dart';
import '../models/plan_model.dart';

class MapSection extends StatefulWidget {
  final List<POI> pois;
  final List<PlanOption> planOptions;
  final int selectedOptionIndex;

  const MapSection({
    super.key,
    required this.pois,
    required this.planOptions,
    required this.selectedOptionIndex,
  });

  @override
  State<MapSection> createState() => _MapSectionState();
}

class _MapSectionState extends State<MapSection> {
  final MapController _mapController = MapController();
  String? _selectedPoiName;

  @override
  void didUpdateWidget(covariant MapSection oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.pois != oldWidget.pois && widget.pois.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _fitBounds());
    }
  }

  void _fitBounds() {
    if (widget.pois.isEmpty) return;
    final points = widget.pois
        .map((p) => LatLng(p.geoCoordinate.lat, p.geoCoordinate.lng))
        .toList();
    if (points.length == 1) {
      _mapController.move(points.first, 14);
    } else {
      final bounds = LatLngBounds.fromPoints(points);
      _mapController.fitCamera(
        CameraFit.bounds(bounds: bounds, padding: const EdgeInsets.all(50)),
      );
    }
  }

  List<LatLng> _extractRoutePoints(PlanOption option) {
    final points = <LatLng>[];
    for (final day in option.days) {
      for (final block in day.blocks) {
        if (block.pois == null) continue;
        for (final poi in block.pois!) {
          final lat = poi.geoCoordinate.lat;
          final lng = poi.geoCoordinate.lng;
          if (lat != 0 && lng != 0) {
            points.add(LatLng(lat, lng));
          }
        }
      }
    }
    return points;
  }

  Color _markerColor(String poiType) {
    switch (poiType) {
      case 'restaurant':
        return Colors.orange;
      case 'lodge':
        return Colors.blue;
      case 'tourist_destination':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _markerIcon(String poiType) {
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

  int? _visitOrder(POI poi) {
    if (widget.planOptions.isEmpty ||
        widget.selectedOptionIndex >= widget.planOptions.length) {
      return null;
    }
    final option = widget.planOptions[widget.selectedOptionIndex];
    int order = 1;
    for (final day in option.days) {
      for (final block in day.blocks) {
        if (block.pois == null) continue;
        for (final blockPoi in block.pois!) {
          if (blockPoi.name == poi.name) return order;
          order++;
        }
      }
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    if (widget.pois.isEmpty) {
      return _buildEmptyState(context);
    }

    // Deduplicate POIs by name
    final seenNames = <String>{};
    final uniquePois = <POI>[];
    for (final poi in widget.pois) {
      if (seenNames.add(poi.name)) {
        uniquePois.add(poi);
      }
    }

    // Build route polyline
    final routePoints = widget.planOptions.isNotEmpty &&
            widget.selectedOptionIndex < widget.planOptions.length
        ? _extractRoutePoints(widget.planOptions[widget.selectedOptionIndex])
        : <LatLng>[];

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text('Map', style: Theme.of(context).textTheme.titleLarge),
              const Spacer(),
              Chip(
                label: Text('${uniquePois.length} locations'),
                visualDensity: VisualDensity.compact,
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 400,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Stack(
                children: [
                  FlutterMap(
                    mapController: _mapController,
                    options: MapOptions(
                      initialCenter: LatLng(
                        uniquePois.first.geoCoordinate.lat,
                        uniquePois.first.geoCoordinate.lng,
                      ),
                      initialZoom: 12,
                      onTap: (_, __) {
                        setState(() => _selectedPoiName = null);
                      },
                    ),
                    children: [
                      TileLayer(
                        urlTemplate:
                            'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                        userAgentPackageName: 'com.tripplanner.app',
                      ),
                      if (routePoints.length >= 2)
                        PolylineLayer(
                          polylines: [
                            Polyline(
                              points: routePoints,
                              color: Colors.blue.withValues(alpha: 0.7),
                              strokeWidth: 3,
                              pattern: const StrokePattern.dotted(),
                            ),
                          ],
                        ),
                      MarkerLayer(
                        markers: uniquePois.map((poi) {
                          final order = _visitOrder(poi);
                          return Marker(
                            point: LatLng(
                              poi.geoCoordinate.lat,
                              poi.geoCoordinate.lng,
                            ),
                            width: 36,
                            height: 36,
                            child: GestureDetector(
                              onTap: () {
                                setState(() {
                                  _selectedPoiName =
                                      _selectedPoiName == poi.name
                                          ? null
                                          : poi.name;
                                });
                              },
                              child: Stack(
                                clipBehavior: Clip.none,
                                children: [
                                  Container(
                                    decoration: BoxDecoration(
                                      color: _markerColor(poi.poiType),
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                          color: Colors.white, width: 2),
                                      boxShadow: const [
                                        BoxShadow(
                                          color: Colors.black26,
                                          blurRadius: 4,
                                          offset: Offset(0, 2),
                                        ),
                                      ],
                                    ),
                                    child: Center(
                                      child: order != null
                                          ? Text(
                                              '$order',
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 14,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            )
                                          : Icon(
                                              _markerIcon(poi.poiType),
                                              color: Colors.white,
                                              size: 18,
                                            ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                  // Tooltip overlay
                  if (_selectedPoiName != null)
                    _buildTooltip(context, uniquePois),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTooltip(BuildContext context, List<POI> uniquePois) {
    final poi = uniquePois.where((p) => p.name == _selectedPoiName).firstOrNull;
    if (poi == null) return const SizedBox.shrink();

    return Positioned(
      top: 12,
      left: 12,
      right: 12,
      child: Material(
        elevation: 4,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              Icon(
                _markerIcon(poi.poiType),
                color: _markerColor(poi.poiType),
                size: 28,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      poi.name,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    if (poi.address != null && poi.address!.isNotEmpty)
                      Text(
                        poi.address!,
                        style: Theme.of(context).textTheme.bodySmall,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    if (poi.cost.isNotEmpty)
                      Text(
                        poi.cost,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Theme.of(context).colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close, size: 18),
                onPressed: () => setState(() => _selectedPoiName = null),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.map_outlined, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No Locations to Display',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.grey[700],
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Chat with the assistant to discover\npoints of interest for your trip!',
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
