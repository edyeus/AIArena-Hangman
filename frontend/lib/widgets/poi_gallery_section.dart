import 'package:flutter/material.dart';
import '../models/poi_model.dart';

class PoiGallerySection extends StatefulWidget {
  final List<POI> pois;
  const PoiGallerySection({super.key, required this.pois});

  @override
  State<PoiGallerySection> createState() => _PoiGallerySectionState();
}

class _PoiGallerySectionState extends State<PoiGallerySection> {
  int? _hoveredIndex;
  int? _tappedIndex;

  @override
  Widget build(BuildContext context) {
    if (widget.pois.isEmpty) {
      return _buildEmptyState();
    }

    // Flatten all images from all POIs
    final allImages = <(String, POI)>[];
    for (final poi in widget.pois) {
      for (final url in poi.imageUrls) {
        allImages.add((url, poi));
      }
    }

    final crossAxisCount = _getCrossAxisCount(MediaQuery.of(context).size.width);

    // Calculate grid height: rows * tile size + spacing
    final rows = (allImages.length / crossAxisCount).ceil();
    const tileSize = 180.0;
    final gridHeight = rows * tileSize + (rows - 1) * 8.0;

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Points of Interest',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const Spacer(),
              Chip(
                label: Text('${widget.pois.length} POIs'),
                visualDensity: VisualDensity.compact,
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: gridHeight.clamp(200.0, double.infinity),
            child: GridView.builder(
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossAxisCount,
                crossAxisSpacing: 8,
                mainAxisSpacing: 8,
                childAspectRatio: 1.0,
              ),
              itemCount: allImages.length,
              itemBuilder: (context, index) {
                final (url, poi) = allImages[index];
                return _buildPhotoTile(url, poi, index);
              },
            ),
          ),
        ],
      ),
    );
  }

  int _getCrossAxisCount(double width) {
    if (width >= 1200) return 5;
    if (width >= 900) return 4;
    if (width >= 600) return 3;
    return 2;
  }

  Widget _buildPhotoTile(String url, POI poi, int index) {
    final isHovered = _hoveredIndex == index;
    final isTapped = _tappedIndex == index;
    final showOverlay = isHovered || isTapped;

    return MouseRegion(
      onEnter: (_) => setState(() => _hoveredIndex = index),
      onExit: (_) => setState(() => _hoveredIndex = null),
      child: InkWell(
        onTap: () => setState(() => _tappedIndex = isTapped ? null : index),
        child: Stack(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                url,
                fit: BoxFit.cover,
                width: double.infinity,
                height: double.infinity,
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return Container(
                    color: Colors.grey[300],
                    child: const Center(child: CircularProgressIndicator()),
                  );
                },
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    color: Colors.grey[300],
                    child: Icon(Icons.broken_image, color: Colors.grey[600], size: 48),
                  );
                },
              ),
            ),
            AnimatedOpacity(
              opacity: showOverlay ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 200),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.85),
                  borderRadius: BorderRadius.circular(8),
                ),
                padding: const EdgeInsets.all(12),
                child: _buildOverlayContent(poi),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverlayContent(POI poi) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          children: [
            Icon(_getPoiIcon(poi.poiType), size: 16, color: Colors.white),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                poi.name,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            if (poi.cost.isNotEmpty)
              Text(
                poi.cost,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                ),
              ),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          poi.description,
          style: const TextStyle(color: Colors.white, fontSize: 12),
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        ),
        if (poi.address != null) ...[
          const SizedBox(height: 6),
          Row(
            children: [
              const Icon(Icons.location_on, size: 12, color: Colors.white70),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  poi.address!,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 11,
                    fontStyle: FontStyle.italic,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ],
        if (poi.openingHours != null) ...[
          const SizedBox(height: 4),
          Row(
            children: [
              const Icon(Icons.access_time, size: 12, color: Colors.white70),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  poi.openingHours!,
                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ],
      ],
    );
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

  Widget _buildEmptyState() {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.explore_off, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No Points of Interest Yet',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.grey[700],
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Chat with the assistant to discover amazing places!',
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
