# Trip Planner Frontend Design Specification v2.0

**Version:** 2.0
**Date:** 2026-02-05
**Status:** Ready for Implementation
**Author:** Product Team

---

## Executive Summary

This specification defines the complete UI/UX for the Trip Planner frontend—a dual-panel application where users interact with an AI service via chat (right panel) and view structured trip planning data (left panel). The left panel is divided into three horizontally-stacked sections: POIs (photo gallery), Requirements (chip display), and Trip Options (comparative table).

This document supersedes v1.0 and incorporates detailed backend data contracts, responsive behavior rules, and specific implementation guidance for the Flutter frontend developer.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Layout & Responsive Behavior](#2-layout--responsive-behavior)
3. [Backend API Contract](#3-backend-api-contract)
4. [Data Models (Dart)](#4-data-models-dart)
5. [Section Specifications](#5-section-specifications)
   - [5.1 POI Gallery](#51-poi-gallery)
   - [5.2 Requirements Section](#52-requirements-section)
   - [5.3 Trip Options Table](#53-trip-options-table)
   - [5.4 Chat Panel](#54-chat-panel)
6. [State Management](#6-state-management)
7. [Component Hierarchy](#7-component-hierarchy)
8. [Visual Design Guidelines](#8-visual-design-guidelines)
9. [Error Handling & Edge Cases](#9-error-handling--edge-cases)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [Acceptance Criteria](#11-acceptance-criteria)

---

## 1. System Architecture

### 1.1 High-Level Flow

```
User Input (Chat)
  → POST /chat (message + existing pois/requirements/plan)
  → Backend processes (Orchestrator → POI Discovery → Planner)
  → Response JSON { intents, pois, requirements, plan }
  → Update Frontend State
  → Re-render All Sections
```

### 1.2 Technology Stack

- **Frontend:** Flutter (Dart SDK ^3.5.3)
- **UI Framework:** Material 3
- **State Management:** `setState` with StatefulWidget (MVP), migrate to Provider/Riverpod post-MVP
- **HTTP Client:** `http` package
- **Backend:** Flask API at `http://localhost:5000`

### 1.3 Key Design Principles

1. **Mobile-first responsive**: Design for stacked mobile layout first, enhance for side-by-side desktop
2. **Photo-oriented POI display**: ALL images from ALL POIs shown in gallery
3. **Comparative plan display**: Multiple options side-by-side for easy comparison
4. **Offline-aware**: Design for slow/unavailable AI services (loading and error states)
5. **Progressive disclosure**: Don't overwhelm—show complexity only when needed

---

## 2. Layout & Responsive Behavior

### 2.1 Desktop Layout (≥900px width)

```
┌──────────────────────────────────────────────────────────────────────┐
│  AppBar: Trip Planner                                                │
├───────────────────────────────────────┬──────────────────────────────┤
│ LEFT PANEL (flex: 3, 60% width)       │ RIGHT PANEL (flex: 2, 40%)   │
│                                       │                              │
│ ┌───────────────────────────────────┐ │ ┌──────────────────────────┐ │
│ │ POI GALLERY (35% height)          │ │ │ Chat Assistant           │ │
│ │ [Photo grid: 4 cols, hover info]  │ │ │ (Header)                 │ │
│ │                                   │ │ └──────────────────────────┘ │
│ │ [img][img][img][img]              │ │ ┌──────────────────────────┐ │
│ │ [img][img][img][img]              │ │ │                          │ │
│ │ [img][img][img][img]              │ │ │  Chat History            │ │
│ └───────────────────────────────────┘ │ │  (scrollable)            │ │
│                                       │ │                          │ │
│ ┌───────────────────────────────────┐ │ │  [bot] Hi! Tell me...    │ │
│ │ REQUIREMENTS (20% height)         │ │ │  [user] Tokyo 3 days     │ │
│ │ [chip] [chip] [chip]              │ │ │  [bot] Great! POIs...    │ │
│ │ [chip] [chip]                     │ │ │                          │ │
│ └───────────────────────────────────┘ │ └──────────────────────────┘ │
│                                       │ ┌──────────────────────────┐ │
│ ┌───────────────────────────────────┐ │ │ [Text Input + Send Btn]  │ │
│ │ TRIP OPTIONS (45% height)         │ │ └──────────────────────────┘ │
│ │ [Scrollable table: →→→→→→→→→→→]   │ │                              │
│ │ ┌─────┬─────┬─────┐               │ │                              │
│ │ │Opt1 │Opt2 │Opt3 │               │ │                              │
│ │ │Day1 │Day1 │Day1 │               │ │                              │
│ │ │Day2 │Day2 │Day2 │               │ │                              │
│ │ └─────┴─────┴─────┘               │ │                              │
│ └───────────────────────────────────┘ │                              │
└───────────────────────────────────────┴──────────────────────────────┘
```

### 2.2 Mobile Layout (<900px width)

```
┌─────────────────────────────────────┐
│  AppBar: Trip Planner               │
├─────────────────────────────────────┤
│ MAIN VIEW PANEL (55% height)        │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ POI GALLERY (35% of main panel) │ │
│ │ [Photo grid: 2 cols, tap info]  │ │
│ │ [img][img]                      │ │
│ │ [img][img]                      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ REQUIREMENTS (20%)              │ │
│ │ [chip] [chip]                   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ TRIP OPTIONS (45%)              │ │
│ │ [Scroll → → →]                  │ │
│ │ ┌────┬────┬────┐                │ │
│ │ │Op1 │Op2 │Op3 │                │ │
│ │ └────┴────┴────┘                │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ CHAT PANEL (45% height)             │
│ ┌─────────────────────────────────┐ │
│ │ Chat History (scrollable)       │ │
│ │                                 │ │
│ │ [bot] Hi!                       │ │
│ │ [user] Tokyo                    │ │
│ └─────────────────────────────────┘ │
│ [Text Input + Send]                 │
└─────────────────────────────────────┘
```

### 2.3 Breakpoints & Column Configuration

| Screen Width | Layout      | POI Columns | Main Panel | Chat Panel |
|--------------|-------------|-------------|------------|------------|
| < 600px      | Stacked     | 2           | 55% height | 45% height |
| 600-899px    | Stacked     | 3           | 60% height | 40% height |
| ≥ 900px      | Side-by-side| 4           | flex: 3    | flex: 2    |
| ≥ 1200px     | Side-by-side| 5           | flex: 3    | flex: 2    |

### 2.4 Responsive Layout Widget

```dart
// In main.dart MyHomePage.build()
return LayoutBuilder(
  builder: (context, constraints) {
    final bool isWide = constraints.maxWidth >= 900;

    if (isWide) {
      return Row(
        children: [
          Expanded(flex: 3, child: mainPanel),
          VerticalDivider(width: 1, thickness: 1),
          Expanded(flex: 2, child: chatPanel),
        ],
      );
    }

    return Column(
      children: [
        Expanded(child: mainPanel),
        Divider(height: 1, thickness: 1),
        SizedBox(
          height: constraints.maxHeight * 0.45,
          child: chatPanel,
        ),
      ],
    );
  },
);
```

---

## 3. Backend API Contract

### 3.1 Endpoint: POST /chat

**URL:** `http://localhost:5000/chat`

**Request Body:**
```json
{
  "message": "I want to visit Tokyo for 3 days",
  "pois": [ /* existing POI list (optional) */ ],
  "requirements": [ /* existing requirements list (optional) */ ],
  "plan": [ /* existing plan options list (optional) */ ]
}
```

**Response Body:**
```json
{
  "intents": [
    {
      "intent": "Points_Of_Interest",
      "action": "add",
      "value": "Tokyo"
    },
    {
      "intent": "Schedule_Requirement",
      "action": "add",
      "value": "3 day trip"
    },
    {
      "intent": "General_Response",
      "action": "add",
      "value": "I found some great places in Tokyo!"
    }
  ],
  "pois": [
    {
      "name": "Senso-ji Temple",
      "description": "Ancient Buddhist temple in Asakusa",
      "geo_coordinate": { "lat": 35.7148, "lng": 139.7967 },
      "poi_type": "tourist_destination",
      "images": {
        "urls": [
          "https://live.staticflickr.com/...",
          "https://live.staticflickr.com/..."
        ]
      },
      "opening_hours": "Temple: 06:00-17:00",
      "address": "2-3-1 Asakusa, Taito City, Tokyo",
      "special_instructions": "Arrive early to avoid crowds",
      "cost": "Free"
    }
  ],
  "requirements": [
    {
      "description": "3 day trip",
      "priority": "preferred"
    }
  ],
  "plan": [
    {
      "overall_cost": "$4200",
      "general_notes": "A 2-day cultural tour of Tokyo focusing on temples and local cuisine.",
      "days": [
        {
          "highlight": "Explore Asakusa and traditional temples",
          "lodging": "Ryokan in Asakusa",
          "blocks": [
            {
              "time": "9:00 AM - 11:30 AM",
              "description": "Visit Senso-ji temple and walk through Nakamise shopping street",
              "pois": [
                {
                  "name": "Senso-ji Temple",
                  "description": "Ancient Buddhist temple in Asakusa",
                  "geo_coordinate": { "lat": 35.7148, "lng": 139.7929 }
                }
              ],
              "transportation": {
                "duration": "10 minutes",
                "method": "walking",
                "cost": 3.5
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### 3.2 Intent Types

- `Points_Of_Interest` — POI discovery request
- `Schedule_Requirement` — Timing/preference constraint
- `Schedule_Option` — Plan modification request
- `General_Response` — Conversational response (display in chat)
- `Not_Relevant` — Out-of-scope input

### 3.3 Priority Enum

- `must_have` — Red, high priority
- `preferred` — Blue, standard priority (default)
- `avoid` — Orange, negative priority

---

## 4. Data Models (Dart)

### 4.1 POI Data Model

**File:** `lib/models/poi_model.dart`

```dart
class GeoCoordinate {
  final double lat;
  final double lng;

  GeoCoordinate({required this.lat, required this.lng});

  factory GeoCoordinate.fromJson(Map<String, dynamic> json) {
    return GeoCoordinate(
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {'lat': lat, 'lng': lng};
}

class POI {
  final String name;
  final String description;
  final GeoCoordinate geoCoordinate;
  final String poiType; // "restaurant", "lodge", "tourist_destination", "unknown"
  final List<String> imageUrls;
  final String? openingHours;
  final String? address;
  final String? specialInstructions;
  final String cost;

  POI({
    required this.name,
    required this.description,
    required this.geoCoordinate,
    required this.poiType,
    required this.imageUrls,
    this.openingHours,
    this.address,
    this.specialInstructions,
    this.cost = '',
  });

  factory POI.fromJson(Map<String, dynamic> json) {
    final geoCoord = json['geo_coordinate'] as Map<String, dynamic>;
    final images = json['images'] as Map<String, dynamic>?;
    final urls = (images?['urls'] as List<dynamic>?)?.cast<String>() ?? [];

    return POI(
      name: json['name'] as String,
      description: json['description'] as String,
      geoCoordinate: GeoCoordinate.fromJson(geoCoord),
      poiType: json['poi_type'] as String? ?? 'unknown',
      imageUrls: urls,
      openingHours: json['opening_hours'] as String?,
      address: json['address'] as String?,
      specialInstructions: json['special_instructions'] as String?,
      cost: json['cost'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'description': description,
    'geo_coordinate': geoCoordinate.toJson(),
    'poi_type': poiType,
    'images': {'urls': imageUrls},
    if (openingHours != null) 'opening_hours': openingHours,
    if (address != null) 'address': address,
    if (specialInstructions != null) 'special_instructions': specialInstructions,
    'cost': cost,
  };
}
```

### 4.2 Requirement Data Model

**File:** `lib/models/requirement_model.dart`

```dart
enum Priority {
  mustHave('must_have'),
  preferred('preferred'),
  avoid('avoid');

  final String value;
  const Priority(this.value);

  static Priority fromString(String value) {
    return Priority.values.firstWhere(
      (p) => p.value == value,
      orElse: () => Priority.preferred,
    );
  }
}

class Requirement {
  final String description;
  final Priority priority;

  Requirement({
    required this.description,
    required this.priority,
  });

  factory Requirement.fromJson(Map<String, dynamic> json) {
    return Requirement(
      description: json['description'] as String,
      priority: Priority.fromString(json['priority'] as String? ?? 'preferred'),
    );
  }

  Map<String, dynamic> toJson() => {
    'description': description,
    'priority': priority.value,
  };
}
```

### 4.3 Plan Option Data Model

**File:** `lib/models/plan_model.dart`

```dart
class Transportation {
  final String duration;
  final String method;
  final double? cost;

  Transportation({
    required this.duration,
    required this.method,
    this.cost,
  });

  factory Transportation.fromJson(Map<String, dynamic> json) {
    return Transportation(
      duration: json['duration'] as String,
      method: json['method'] as String,
      cost: (json['cost'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
    'duration': duration,
    'method': method,
    if (cost != null) 'cost': cost,
  };
}

class Block {
  final String time;
  final String description;
  final List<POI>? pois;
  final Transportation? transportation;

  Block({
    required this.time,
    required this.description,
    this.pois,
    this.transportation,
  });

  factory Block.fromJson(Map<String, dynamic> json) {
    final poisJson = json['pois'] as List<dynamic>?;
    final transportJson = json['transportation'] as Map<String, dynamic>?;

    return Block(
      time: json['time'] as String,
      description: json['description'] as String,
      pois: poisJson?.map((p) => POI.fromJson(p as Map<String, dynamic>)).toList(),
      transportation: transportJson != null ? Transportation.fromJson(transportJson) : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'time': time,
    'description': description,
    if (pois != null) 'pois': pois!.map((p) => p.toJson()).toList(),
    if (transportation != null) 'transportation': transportation!.toJson(),
  };
}

class Day {
  final String highlight;
  final String? lodging;
  final List<Block> blocks;

  Day({
    required this.highlight,
    this.lodging,
    required this.blocks,
  });

  factory Day.fromJson(Map<String, dynamic> json) {
    final blocksJson = json['blocks'] as List<dynamic>;
    return Day(
      highlight: json['highlight'] as String,
      lodging: json['lodging'] as String?,
      blocks: blocksJson.map((b) => Block.fromJson(b as Map<String, dynamic>)).toList(),
    );
  }

  Map<String, dynamic> toJson() => {
    'highlight': highlight,
    if (lodging != null) 'lodging': lodging,
    'blocks': blocks.map((b) => b.toJson()).toList(),
  };
}

class PlanOption {
  final String overallCost;
  final String generalNotes;
  final List<Day> days;

  PlanOption({
    required this.overallCost,
    required this.generalNotes,
    required this.days,
  });

  factory PlanOption.fromJson(Map<String, dynamic> json) {
    final daysJson = json['days'] as List<dynamic>;
    return PlanOption(
      overallCost: json['overall_cost'] as String,
      generalNotes: json['general_notes'] as String,
      days: daysJson.map((d) => Day.fromJson(d as Map<String, dynamic>)).toList(),
    );
  }

  Map<String, dynamic> toJson() => {
    'overall_cost': overallCost,
    'general_notes': generalNotes,
    'days': days.map((d) => d.toJson()).toList(),
  };
}
```

### 4.4 Chat Message Model

**File:** `lib/models/chat_model.dart`

```dart
class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.text,
    required this.isUser,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class Intent {
  final String intent;
  final String action;
  final String value;

  Intent({
    required this.intent,
    required this.action,
    required this.value,
  });

  factory Intent.fromJson(Map<String, dynamic> json) {
    return Intent(
      intent: json['intent'] as String,
      action: json['action'] as String,
      value: json['value'] as String,
    );
  }
}
```

---

## 5. Section Specifications

## 5.1 POI Gallery

### 5.1.1 Purpose

Display all POIs returned by the backend in a **very photo-oriented** grid. Show ALL photos for ALL POIs. On mouse hover (desktop) or tap (mobile), display an overlay with POI metadata.

### 5.1.2 Layout

**Grid Configuration:**
- Desktop (≥1200px): 5 columns
- Desktop (900-1199px): 4 columns
- Tablet (600-899px): 3 columns
- Mobile (<600px): 2 columns
- Grid spacing: 8px
- Aspect ratio: 1:1 (square tiles)

**Container:**
- Background: `Theme.of(context).colorScheme.surface`
- Padding: 16px
- Border radius: 12px
- Minimum height: 200px

### 5.1.3 Photo Tile

Each photo tile is a `Stack` with:

1. **Background Image:**
   - `CachedNetworkImage` or `Image.network`
   - `fit: BoxFit.cover`
   - Border radius: 8px
   - Loading: shimmer or circular progress
   - Error: gray placeholder with `Icons.broken_image`

2. **Hover/Tap Overlay:**
   - Semi-transparent black overlay (opacity: 0.85)
   - Animation: fade in/out (200ms)
   - Trigger: `MouseRegion` (desktop) or `InkWell.onTap` (mobile)

**Overlay Content:**
```
┌────────────────────────┐
│ [icon] POI Name   $15  │  <- icon = poi_type, cost at top-right
│                        │
│ Description text here  │
│ up to 3 lines with...  │
│                        │
│ 📍 Address (1 line)    │
│ 🕐 Opening hours       │
└────────────────────────┘
```

### 5.1.4 Widget Structure

```dart
class PoiGallerySection extends StatefulWidget {
  final List<POI> pois;
  const PoiGallerySection({Key? key, required this.pois}) : super(key: key);

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

    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
      ),
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
          Expanded(
            child: GridView.builder(
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
                    child: Center(child: CircularProgressIndicator()),
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
                  color: Colors.black.withOpacity(0.85),
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
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(12),
      ),
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
```

### 5.1.5 Empty State

Center-aligned icon and text encouraging user to start chatting.

### 5.1.6 Loading State

Show 8-12 shimmer placeholder tiles in grid.

---

## 5.2 Requirements Section

### 5.2.1 Purpose

Display user requirements as color-coded, non-interactive chips. Visual feedback on constraints being considered by the planner.

### 5.2.2 Layout

- Container: `surfaceVariant` background, 16px padding, 12px radius
- Minimum height: 80px
- Chips wrapped using `Wrap` widget (spacing: 8px, runSpacing: 8px)

### 5.2.3 Chip Design

**Priority Colors:**
- `must_have`: Red/error color (red.shade100 bg, red.shade800 text)
- `preferred`: Blue/primary color (blue.shade100 bg, blue.shade800 text)
- `avoid`: Orange/warning color (orange.shade100 bg, orange.shade800 text)

**Chip Structure:**
- Avatar icon: priority-specific icon
- Label: requirement description
- Padding: 8px horizontal, 6px vertical

**Icon Mapping:**
- `must_have`: `Icons.star`
- `preferred`: `Icons.favorite_border`
- `avoid`: `Icons.block`

### 5.2.4 Widget Structure

```dart
class RequirementsSection extends StatelessWidget {
  final List<Requirement> requirements;
  const RequirementsSection({Key? key, required this.requirements}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (requirements.isEmpty) {
      return _buildEmptyState(context);
    }

    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(16),
      constraints: const BoxConstraints(minHeight: 80),
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
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(32),
      constraints: const BoxConstraints(minHeight: 80),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.checklist, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 12),
            Text(
              'No requirements captured yet',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            Text(
              'Tell the assistant your preferences!',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

### 5.2.5 Empty State

Center-aligned icon and text.

### 5.2.6 Loading State

Show 3-4 shimmer chips.

---

## 5.3 Trip Options Table

### 5.3.1 Purpose

Display multiple itinerary options in a **nice-looking table format** that allows vertical comparison. Each option is a column. If the screen is not large enough, the section should be **left-right scrollable**.

### 5.3.2 Layout

- Horizontal `SingleChildScrollView` containing a `Row` of option cards
- Each option card: fixed width 320px, full height of container
- Card spacing: 16px horizontal
- Scroll indicators visible

### 5.3.3 Option Card Structure

```
┌──────────────────────────────┐
│ OPTION 1         $4200       │ <- Header (primaryContainer)
│ Cultural tour focusing...    │
├──────────────────────────────┤
│ Day 1: Explore Asakusa       │ <- Scrollable list of days
│ 🛏 Ryokan in Asakusa          │
│                              │
│ 9:00-11:30                   │ <- Time blocks
│ Visit Senso-ji temple        │
│ 🚶 10 min walking            │
│                              │
│ 12:00-13:00                  │
│ Lunch at soba restaurant     │
│                              │
├──────────────────────────────┤
│ Day 2: Modern Tokyo          │
│ 🛏 Hotel in Shinjuku         │
│ ...                          │
└──────────────────────────────┘
```

### 5.3.4 Widget Structure

```dart
class TripOptionsSection extends StatelessWidget {
  final List<PlanOption> planOptions;
  const TripOptionsSection({Key? key, required this.planOptions}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (planOptions.isEmpty) {
      return _buildEmptyState(context);
    }

    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(12),
      ),
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
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: planOptions.asMap().entries.map((entry) {
                  final index = entry.key;
                  final option = entry.value;
                  return Padding(
                    padding: EdgeInsets.only(right: index < planOptions.length - 1 ? 16 : 0),
                    child: _buildOptionCard(context, option, index + 1),
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOptionCard(BuildContext context, PlanOption option, int optionNumber) {
    return Container(
      width: 320,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Theme.of(context).dividerColor, width: 1),
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
                  _getTransportIcon(block.transportation!.method),
                  size: 16,
                  color: Theme.of(context).colorScheme.secondary,
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    '${block.transportation!.duration} · ${block.transportation!.method}',
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
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(12),
      ),
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
```

### 5.3.5 Empty State

Center-aligned icon and text.

### 5.3.6 Loading State

Show 2-3 shimmer option cards.

---

## 5.4 Chat Panel

### 5.4.1 Purpose

User input interface for conversing with the backend AI. Already partially implemented.

### 5.4.2 Modifications Needed

1. **Replace hardcoded messages** with dynamic list from state
2. **Add loading indicator** (show "Analyzing your request..." while `isLoading` is true)
3. **Wire up send button** to callback
4. **Auto-scroll** to bottom on new message

### 5.4.3 Updated Widget

```dart
class ChatViewPanel extends StatefulWidget {
  final TextEditingController controller;
  final List<ChatMessage> messages;
  final bool isLoading;
  final Function(String) onSendMessage;

  const ChatViewPanel({
    Key? key,
    required this.controller,
    required this.messages,
    required this.isLoading,
    required this.onSendMessage,
  }) : super(key: key);

  @override
  State<ChatViewPanel> createState() => _ChatViewPanelState();
}

class _ChatViewPanelState extends State<ChatViewPanel> {
  final ScrollController _scrollController = ScrollController();

  @override
  void didUpdateWidget(ChatViewPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.messages.length != oldWidget.messages.length) {
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.surfaceVariant,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        children: [
          Row(
            children: [
              Text('Chat Assistant', style: Theme.of(context).textTheme.titleLarge),
              const Spacer(),
              Icon(Icons.chat_bubble_outline, color: Theme.of(context).colorScheme.primary),
            ],
          ),
          const SizedBox(height: 12),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              itemCount: widget.messages.length + (widget.isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (widget.isLoading && index == widget.messages.length) {
                  return const ChatBubble(
                    text: 'Analyzing your request...',
                    isUser: false,
                  );
                }
                final message = widget.messages[index];
                return ChatBubble(
                  text: message.text,
                  isUser: message.isUser,
                );
              },
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: widget.controller,
                    minLines: 1,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      hintText: 'Ask about routes, dates, budgets...',
                      border: InputBorder.none,
                    ),
                    onSubmitted: widget.isLoading ? null : (text) {
                      if (text.trim().isNotEmpty) {
                        widget.onSendMessage(text);
                      }
                    },
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: widget.isLoading ? null : () {
                    final text = widget.controller.text;
                    if (text.trim().isNotEmpty) {
                      widget.onSendMessage(text);
                    }
                  },
                  child: const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## 6. State Management

### 6.1 Approach: setState + StatefulWidget (MVP)

For pre-MVP, use Flutter's built-in state management. All state lives in `_MyHomePageState`.

### 6.2 State Structure

```dart
class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _chatController = TextEditingController();
  final List<ChatMessage> _messages = [];
  List<POI> _pois = [];
  List<Requirement> _requirements = [];
  List<PlanOption> _planOptions = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _messages.add(ChatMessage(
      text: 'Hi! Tell me your destination, dates, and preferences.',
      isUser: false,
    ));
  }

  Future<void> _sendMessage(String message) async {
    if (message.trim().isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(text: message, isUser: true));
      _isLoading = true;
    });
    _chatController.clear();

    try {
      final response = await http.post(
        Uri.parse('http://localhost:5000/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'message': message,
          'pois': _pois.map((p) => p.toJson()).toList(),
          'requirements': _requirements.map((r) => r.toJson()).toList(),
          'plan': _planOptions.map((p) => p.toJson()).toList(),
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        _processResponse(data);
      } else {
        _addErrorMessage('Sorry, I encountered an error. Please try again.');
      }
    } catch (e) {
      _addErrorMessage('Network error. Please check your connection.');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _processResponse(Map<String, dynamic> data) {
    // Extract General_Response intents for chat
    final intents = data['intents'] as List<dynamic>? ?? [];
    final generalResponses = intents
        .where((i) => (i as Map<String, dynamic>)['intent'] == 'General_Response')
        .map((i) => (i as Map<String, dynamic>)['value'] as String?)
        .where((text) => text != null && text.isNotEmpty)
        .join('\n\n');

    setState(() {
      if (generalResponses.isNotEmpty) {
        _messages.add(ChatMessage(text: generalResponses, isUser: false));
      }

      // Update POIs
      if (data['pois'] != null) {
        final newPOIs = (data['pois'] as List<dynamic>)
            .map((p) => POI.fromJson(p as Map<String, dynamic>))
            .toList();
        _mergePOIs(newPOIs);
      }

      // Update Requirements
      if (data['requirements'] != null) {
        final newReqs = (data['requirements'] as List<dynamic>)
            .map((r) => Requirement.fromJson(r as Map<String, dynamic>))
            .toList();
        _mergeRequirements(newReqs);
      }

      // Replace Plan Options
      if (data['plan'] != null) {
        _planOptions = (data['plan'] as List<dynamic>)
            .map((p) => PlanOption.fromJson(p as Map<String, dynamic>))
            .toList();
      }
    });
  }

  void _mergePOIs(List<POI> newPOIs) {
    final existingNames = _pois.map((p) => p.name.toLowerCase()).toSet();
    final uniqueNew = newPOIs.where((p) => !existingNames.contains(p.name.toLowerCase())).toList();
    _pois.addAll(uniqueNew);
  }

  void _mergeRequirements(List<Requirement> newReqs) {
    final existingDescs = _requirements.map((r) => r.description.toLowerCase()).toSet();
    final uniqueNew = newReqs.where((r) => !existingDescs.contains(r.description.toLowerCase())).toList();
    _requirements.addAll(uniqueNew);
  }

  void _addErrorMessage(String text) {
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: false));
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Trip Planner'),
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final bool isWide = constraints.maxWidth >= 900;
          final mainPanel = MainViewPanel(
            pois: _pois,
            requirements: _requirements,
            planOptions: _planOptions,
          );
          final chatPanel = ChatViewPanel(
            controller: _chatController,
            messages: _messages,
            isLoading: _isLoading,
            onSendMessage: _sendMessage,
          );

          if (isWide) {
            return Row(
              children: [
                Expanded(flex: 3, child: mainPanel),
                const VerticalDivider(width: 1, thickness: 1),
                Expanded(flex: 2, child: chatPanel),
              ],
            );
          }

          return Column(
            children: [
              Expanded(child: mainPanel),
              const Divider(height: 1, thickness: 1),
              SizedBox(
                height: constraints.maxHeight * 0.45,
                child: chatPanel,
              ),
            ],
          );
        },
      ),
    );
  }
}
```

---

## 7. Component Hierarchy

### 7.1 File Structure

```
frontend/lib/
├── main.dart                          # Root app + MyHomePage (stateful)
├── models/
│   ├── poi_model.dart                 # POI, GeoCoordinate
│   ├── requirement_model.dart         # Requirement, Priority enum
│   ├── plan_model.dart                # PlanOption, Day, Block, Transportation
│   └── chat_model.dart                # ChatMessage, Intent
├── services/
│   └── api_service.dart               # HTTP client (optional, inline in main.dart for MVP)
└── widgets/
    ├── main_view_panel.dart           # Container for 3 sections
    ├── poi_gallery_section.dart       # POI photo grid
    ├── requirements_section.dart      # Requirements chips
    ├── trip_options_section.dart      # Trip options table
    ├── chat_view_panel.dart           # Chat UI (modified)
    └── chat_bubble.dart               # Chat message bubble (unchanged)
```

### 7.2 Widget Tree

```
MyApp
└── MaterialApp
    └── MyHomePage (StatefulWidget)
        └── Scaffold
            ├── AppBar
            └── LayoutBuilder
                └── Row (wide) | Column (narrow)
                    ├── MainViewPanel (StatelessWidget)
                    │   └── Column
                    │       ├── Header
                    │       └── Expanded Column
                    │           ├── Expanded (flex: 35) → PoiGallerySection
                    │           ├── SizedBox(height: 16)
                    │           ├── Expanded (flex: 20) → RequirementsSection
                    │           ├── SizedBox(height: 16)
                    │           └── Expanded (flex: 45) → TripOptionsSection
                    └── ChatViewPanel (StatefulWidget)
                        └── Column
                            ├── Header Row
                            ├── Expanded ListView (messages)
                            └── Input Container (TextField + Button)
```

---

## 8. Visual Design Guidelines

### 8.1 Color Palette (Material 3)

- **Primary**: `Colors.deepPurple` (customizable via seed color)
- **Surface**: Light background for main content
- **SurfaceVariant**: Slightly darker for sections
- **PrimaryContainer**: Highlighted areas (option headers)

### 8.2 Typography

- **headlineMedium**: Section titles (24sp)
- **titleLarge**: Sub-section headers (22sp)
- **titleMedium**: Card titles (16sp)
- **bodyLarge**: Primary content (16sp)
- **bodyMedium**: Standard text (14sp)
- **bodySmall**: Captions (12sp)
- **labelLarge**: Labels (14sp)

### 8.3 Spacing

- Section padding: 24px
- Inter-section spacing: 16px
- Card padding: 16px
- Chip spacing: 8px
- Grid spacing: 8px

### 8.4 Border Radius

- Cards: 12px
- Chips: 20px (pill)
- Input fields: 14px
- Images: 8px

### 8.5 Elevation

- Cards: elevation 2
- Hoverable items: elevation 4 on hover
- Modals: elevation 8

### 8.6 Animations

- Hover overlay: fade (200ms)
- Chat scroll: animate (300ms)
- Loading: shimmer (1500ms loop)

---

## 9. Error Handling & Edge Cases

### 9.1 Network Errors

- Show error message in chat
- Keep existing data intact
- Disable send button while loading

### 9.2 Empty States

- All sections have empty state UI
- Encourage user action with clear messaging

### 9.3 Image Loading Failures

- Show placeholder with broken image icon
- Maintain grid layout

### 9.4 Large Datasets

- Use `GridView.builder` and `ListView.builder` for performance
- Images load lazily

### 9.5 Duplicate Data

- Deduplicate POIs by name (case-insensitive)
- Deduplicate requirements by description (case-insensitive)
- Plan options are always replaced (not merged)

### 9.6 Mobile Hover Behavior

- Use `InkWell.onTap` to toggle overlay on mobile
- Store tapped index in state

---

## 10. Implementation Roadmap

### Phase 1: Foundation (4-6 hours)
1. Create data models
2. Modify `_MyHomePageState` with API integration

### Phase 2: Chat Enhancement (3-4 hours)
3. Update `ChatViewPanel`
4. Add loading state and auto-scroll

### Phase 3: Main View Restructure (2-3 hours)
5. Create section containers with empty states
6. Modify `MainViewPanel`

### Phase 4: POI Gallery (6-8 hours)
7. Implement photo grid with hover overlays
8. Add mobile tap behavior

### Phase 5: Requirements (2-3 hours)
9. Implement chip layout

### Phase 6: Trip Options (8-10 hours)
10. Create option cards, day cards, time blocks
11. Implement horizontal scroll

### Phase 7: Polish (6-8 hours)
12. Add loading states, error handling
13. Performance testing

### Phase 8: Testing (4-6 hours)
14. End-to-end testing
15. Cross-browser testing

**Total: 37-50 hours**

---

## 11. Acceptance Criteria

### Functional
- [ ] User can send messages and receive responses
- [ ] POIs displayed in photo grid with hover/tap overlays
- [ ] Requirements displayed as color-coded chips
- [ ] Trip options displayed in comparative table
- [ ] Data accumulates across chat interactions
- [ ] Responsive layout at 900px breakpoint
- [ ] Loading, empty, and error states work

### Visual
- [ ] Consistent Material 3 theming
- [ ] Proper spacing and alignment
- [ ] Text truncates gracefully
- [ ] Images load with placeholders
- [ ] Smooth animations

### Technical
- [ ] No console errors
- [ ] Handles large datasets
- [ ] Proper error handling
- [ ] Clean state management

### Responsive
- [ ] Works on desktop (1920px+)
- [ ] Works on laptop (1366-1920px)
- [ ] Works on tablet (768-1024px)
- [ ] Works on mobile (375-768px)

---

**End of Design Specification v2.0**
