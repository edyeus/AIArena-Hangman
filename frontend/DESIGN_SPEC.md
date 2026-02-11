# Trip Planner Frontend Design Specification

Version: 1.0
Date: 2026-02-05
Status: Ready for Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Layout Architecture](#layout-architecture)
3. [Right Section: Chat UI](#right-section-chat-ui)
4. [Left Section: Trip Planner](#left-section-trip-planner)
   - [Sub-section 1: POI Gallery](#sub-section-1-poi-gallery)
   - [Sub-section 2: Requirements](#sub-section-2-requirements)
   - [Sub-section 3: Trip Options](#sub-section-3-trip-options)
5. [Data Flow & Backend Integration](#data-flow--backend-integration)
6. [Responsive Behavior](#responsive-behavior)
7. [State Management](#state-management)
8. [Component Hierarchy](#component-hierarchy)
9. [Visual Design Guidelines](#visual-design-guidelines)
10. [Edge Cases](#edge-cases)

---

## Overview

This specification defines the UI/UX for the Trip Planner frontend, which consists of two main sections:
- **Right section**: Chat interface for user interaction with the backend AI service
- **Left section**: Trip planner display with three vertically stacked sub-sections (POIs, Requirements, Trip Options)

The frontend integrates with a Flask backend that returns structured data via the `/chat` endpoint.

---

## Layout Architecture

### High-Level Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ AppBar: Trip Planner                                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────┬──────────────────────────────────┐│
│  │                             │                                  ││
│  │  LEFT SECTION               │  RIGHT SECTION                   ││
│  │  (Trip Planner)             │  (Chat UI)                       ││
│  │                             │                                  ││
│  │  ┌───────────────────────┐  │  ┌────────────────────────────┐ ││
│  │  │ 1. POI Gallery        │  │  │ Chat History (scrollable)  │ ││
│  │  │ (scrollable)          │  │  │                            │ ││
│  │  └───────────────────────┘  │  │ [bot] Hi! Tell me...       │ ││
│  │                             │  │ [user] Tokyo in April      │ ││
│  │  ┌───────────────────────┐  │  │ [bot] Great! Do you...     │ ││
│  │  │ 2. Requirements       │  │  └────────────────────────────┘ ││
│  │  └───────────────────────┘  │                                  ││
│  │                             │  ┌────────────────────────────┐ ││
│  │  ┌───────────────────────┐  │  │ Text Input + Send Button   │ ││
│  │  │ 3. Trip Options       │  │  └────────────────────────────┘ ││
│  │  │ (scrollable)          │  │                                  ││
│  │  └───────────────────────┘  │                                  ││
│  │                             │                                  ││
│  └─────────────────────────────┴──────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Width >= 900px (Desktop/Wide)
- **Left section**: 60% width (flex: 3)
- **Right section**: 40% width (flex: 2)
- Sections arranged side-by-side in a `Row`
- 1px vertical divider between sections

### Width < 900px (Mobile/Narrow)
- **Top section**: Left panel (Trip Planner) - 55% height
- **Bottom section**: Right panel (Chat) - 45% height
- Sections arranged vertically in a `Column`
- 1px horizontal divider between sections

---

## Right Section: Chat UI

### Current Implementation
The `ChatViewPanel` widget already exists at `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/chat_view_panel.dart`.

### Required Modifications

#### 1. Add State Management for Chat Messages
- Replace the hardcoded `ChatBubble` list with a dynamic list managed by state
- Accept a callback function for sending messages

#### 2. Add Loading State
- Show a loading indicator when waiting for backend response
- Loading indicator should appear as a system message bubble: "Analyzing your request..."

#### 3. Wire Up Send Button
The `FilledButton` at line 70 currently has an empty `onPressed` handler. It should:
- Trigger a callback to send the message to the backend
- Clear the text field after sending
- Add the user message to the chat history immediately
- Show loading state while waiting for response

#### 4. Auto-Scroll Behavior
- When a new message is added, automatically scroll to the bottom
- Use `ScrollController` and `animateTo()` for smooth scrolling

### Widget Signature (Modified)

```dart
class ChatViewPanel extends StatefulWidget {
  const ChatViewPanel({
    super.key,
    required this.controller,
    required this.messages,
    required this.onSendMessage,
    this.isLoading = false,
  });

  final TextEditingController controller;
  final List<ChatMessage> messages;
  final Function(String) onSendMessage;
  final bool isLoading;

  @override
  State<ChatViewPanel> createState() => _ChatViewPanelState();
}
```

### Data Model: ChatMessage

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
```

### Interaction Flow

1. User types message in text field
2. User presses Send button (or Enter key)
3. Message is immediately added to chat history as user message
4. Text field is cleared
5. Loading indicator appears
6. Backend request is sent via parent widget callback
7. When response arrives, loading indicator is replaced with bot response
8. Chat auto-scrolls to bottom

---

## Left Section: Trip Planner

The `MainViewPanel` widget currently exists as a placeholder. It needs to be completely redesigned to show three vertically stacked sub-sections.

### New Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Trip Planner Header                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ POI Gallery (height: 35% of available space)     │ │
│  │ [Photo grid with hover overlays]                 │ │
│  │ [Horizontal scroll if needed]                    │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Requirements (height: 20% of available space)    │ │
│  │ [Chips/bubbles showing requirements]             │ │
│  │ [Wrapping layout]                                │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Trip Options (height: 45% of available space)    │ │
│  │ [Comparative table of plan options]              │ │
│  │ [Horizontal scroll if wide]                      │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Widget Signature (Modified)

```dart
class MainViewPanel extends StatelessWidget {
  const MainViewPanel({
    super.key,
    required this.pois,
    required this.requirements,
    required this.planOptions,
  });

  final List<POIData> pois;
  final List<RequirementData> requirements;
  final List<PlanOptionData> planOptions;

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
            child: Column(
              children: [
                // POI Gallery (35%)
                Expanded(
                  flex: 35,
                  child: POIGallerySection(pois: pois),
                ),
                const SizedBox(height: 16),
                // Requirements (20%)
                Expanded(
                  flex: 20,
                  child: RequirementsSection(requirements: requirements),
                ),
                const SizedBox(height: 16),
                // Trip Options (45%)
                Expanded(
                  flex: 45,
                  child: TripOptionsSection(planOptions: planOptions),
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

## Sub-section 1: POI Gallery

### Purpose
Display all POIs returned by the backend with a strong visual emphasis on photos. Users should be able to browse all POI images in a grid and hover to see details.

### Data Model: POIData

```dart
class POIData {
  final String name;
  final String description;
  final double lat;
  final double lng;
  final String poiType; // "restaurant", "lodge", "tourist_destination", "unknown"
  final List<String> imageUrls;
  final String? openingHours;
  final String? address;
  final String? specialInstructions;
  final String? cost;

  POIData({
    required this.name,
    required this.description,
    required this.lat,
    required this.lng,
    required this.poiType,
    required this.imageUrls,
    this.openingHours,
    this.address,
    this.specialInstructions,
    this.cost,
  });

  factory POIData.fromJson(Map<String, dynamic> json) {
    final geoCoord = json['geo_coordinate'] as Map<String, dynamic>;
    final images = json['images'] as Map<String, dynamic>?;
    final urls = images?['urls'] as List<dynamic>? ?? [];

    return POIData(
      name: json['name'] as String,
      description: json['description'] as String,
      lat: (geoCoord['lat'] as num).toDouble(),
      lng: (geoCoord['lng'] as num).toDouble(),
      poiType: json['poi_type'] as String? ?? 'unknown',
      imageUrls: urls.cast<String>(),
      openingHours: json['opening_hours'] as String?,
      address: json['address'] as String?,
      specialInstructions: json['special_instructions'] as String?,
      cost: json['cost'] as String?,
    );
  }
}
```

### UI Layout

#### Photo Grid
- Display ALL photos from ALL POIs in a single continuous grid
- Use `GridView.builder` with `crossAxisCount` that adapts to screen width:
  - Width >= 1200px: 5 columns
  - Width >= 900px: 4 columns
  - Width >= 600px: 3 columns
  - Width < 600px: 2 columns
- Grid spacing: 8px between items
- Each photo should maintain aspect ratio (use `AspectRatio(aspectRatio: 1.0)` for square tiles)

#### Photo Tile
Each photo tile consists of:
- Image displayed using `Image.network` with:
  - `fit: BoxFit.cover`
  - `loadingBuilder` for progressive loading
  - `errorBuilder` for failed loads (show placeholder icon)
- Rounded corners: `BorderRadius.circular(8)`
- Elevation/shadow for depth

#### Hover Overlay
On hover (or tap on mobile), show an overlay with POI information:
- Semi-transparent dark overlay (opacity: 0.85)
- POI name (bold, white text, 16px)
- POI description (white text, 14px, max 3 lines with ellipsis)
- POI type icon (restaurant, lodge, tourist_destination)
- Address (if available, white text, 12px, italic)
- Opening hours (if available, white text, 12px)
- Cost (if available, white text, 14px, bold, positioned at top-right corner)

Use `MouseRegion` (for web/desktop) or `InkWell` with `onTap` (for mobile) to detect interaction.

#### Hover Overlay Layout

```dart
Stack(
  children: [
    // Background image
    Image.network(url),
    // Hover overlay
    MouseRegion(
      onEnter: (_) => setState(() => _hoveredIndex = index),
      onExit: (_) => setState(() => _hoveredIndex = null),
      child: AnimatedOpacity(
        opacity: _hoveredIndex == index ? 1.0 : 0.0,
        duration: const Duration(milliseconds: 200),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.85),
            borderRadius: BorderRadius.circular(8),
          ),
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(_getPoiIcon(poiType), size: 20, color: Colors.white),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (cost != null && cost.isNotEmpty)
                    Text(
                      cost,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: const TextStyle(color: Colors.white, fontSize: 14),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              if (address != null) ...[
                const SizedBox(height: 8),
                Text(
                  address!,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              if (openingHours != null) ...[
                const SizedBox(height: 4),
                Text(
                  openingHours!,
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ],
          ),
        ),
      ),
    ),
  ],
)
```

#### Icon Mapping for POI Types

```dart
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
```

### Empty State
If no POIs are available:
```
┌─────────────────────────────────────┐
│                                     │
│         [Icon: explore_off]         │
│                                     │
│     No Points of Interest Yet       │
│                                     │
│  Chat with the assistant to         │
│  discover amazing places!           │
│                                     │
└─────────────────────────────────────┘
```

### Loading State
While POIs are being fetched:
- Show a grid of shimmer placeholders (8 tiles)
- Use `Shimmer` package or `AnimatedContainer` with gradient

---

## Sub-section 2: Requirements

### Purpose
Display the list of requirements distilled from user input. These are read-only chips/bubbles that summarize constraints and preferences.

### Data Model: RequirementData

```dart
class RequirementData {
  final String description;
  final String priority; // "must_have", "preferred", "avoid"

  RequirementData({
    required this.description,
    required this.priority,
  });

  factory RequirementData.fromJson(Map<String, dynamic> json) {
    return RequirementData(
      description: json['description'] as String,
      priority: json['priority'] as String? ?? 'preferred',
    );
  }
}
```

### UI Layout

#### Container
- Background: `Theme.of(context).colorScheme.surfaceVariant`
- Padding: 16px all sides
- Border radius: 12px
- Minimum height: 80px (to prevent collapse when empty)

#### Chip Layout
- Use `Wrap` widget for automatic wrapping of chips
- `spacing`: 8px (horizontal space between chips)
- `runSpacing`: 8px (vertical space between rows)

#### Individual Chip Style
Each requirement is displayed as a `Chip` with color-coded priority:
- **Must Have**: Red accent color (`Colors.red.shade100` background, `Colors.red.shade800` text)
- **Preferred**: Blue accent color (`Colors.blue.shade100` background, `Colors.blue.shade800` text)
- **Avoid**: Orange accent color (`Colors.orange.shade100` background, `Colors.orange.shade800` text)

```dart
Chip(
  label: Text(
    requirement.description,
    style: TextStyle(
      color: _getTextColor(requirement.priority),
      fontSize: 14,
    ),
  ),
  backgroundColor: _getBackgroundColor(requirement.priority),
  avatar: Icon(
    _getPriorityIcon(requirement.priority),
    size: 18,
    color: _getTextColor(requirement.priority),
  ),
  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
)
```

#### Color & Icon Mapping

```dart
Color _getBackgroundColor(String priority) {
  switch (priority) {
    case 'must_have':
      return Colors.red.shade100;
    case 'avoid':
      return Colors.orange.shade100;
    case 'preferred':
    default:
      return Colors.blue.shade100;
  }
}

Color _getTextColor(String priority) {
  switch (priority) {
    case 'must_have':
      return Colors.red.shade800;
    case 'avoid':
      return Colors.orange.shade800;
    case 'preferred':
    default:
      return Colors.blue.shade800;
  }
}

IconData _getPriorityIcon(String priority) {
  switch (priority) {
    case 'must_have':
      return Icons.star;
    case 'avoid':
      return Icons.block;
    case 'preferred':
    default:
      return Icons.favorite_border;
  }
}
```

### Empty State
If no requirements are available:
```
┌─────────────────────────────────────┐
│                                     │
│  No requirements captured yet.      │
│  Tell the assistant your            │
│  preferences!                       │
│                                     │
└─────────────────────────────────────┘
```
- Text centered, gray color, 14px
- Icon: `Icons.checklist` above text

---

## Sub-section 3: Trip Options

### Purpose
Display multiple plan options in a comparative table format. Each option contains days, each day contains time blocks with activities/POIs.

### Data Model: PlanOptionData

```dart
class PlanOptionData {
  final String overallCost;
  final String generalNotes;
  final List<DayData> days;

  PlanOptionData({
    required this.overallCost,
    required this.generalNotes,
    required this.days,
  });

  factory PlanOptionData.fromJson(Map<String, dynamic> json) {
    final daysJson = json['days'] as List<dynamic>;
    return PlanOptionData(
      overallCost: json['overall_cost'] as String,
      generalNotes: json['general_notes'] as String,
      days: daysJson.map((d) => DayData.fromJson(d as Map<String, dynamic>)).toList(),
    );
  }
}

class DayData {
  final String highlight;
  final String? lodging;
  final List<BlockData> blocks;

  DayData({
    required this.highlight,
    this.lodging,
    required this.blocks,
  });

  factory DayData.fromJson(Map<String, dynamic> json) {
    final blocksJson = json['blocks'] as List<dynamic>;
    return DayData(
      highlight: json['highlight'] as String,
      lodging: json['lodging'] as String?,
      blocks: blocksJson.map((b) => BlockData.fromJson(b as Map<String, dynamic>)).toList(),
    );
  }
}

class BlockData {
  final String time;
  final String description;
  final List<POIData>? pois;
  final TransportationData? transportation;

  BlockData({
    required this.time,
    required this.description,
    this.pois,
    this.transportation,
  });

  factory BlockData.fromJson(Map<String, dynamic> json) {
    final poisJson = json['pois'] as List<dynamic>?;
    final transportJson = json['transportation'] as Map<String, dynamic>?;

    return BlockData(
      time: json['time'] as String,
      description: json['description'] as String,
      pois: poisJson?.map((p) => POIData.fromJson(p as Map<String, dynamic>)).toList(),
      transportation: transportJson != null ? TransportationData.fromJson(transportJson) : null,
    );
  }
}

class TransportationData {
  final String duration;
  final String method;
  final double? cost;

  TransportationData({
    required this.duration,
    required this.method,
    this.cost,
  });

  factory TransportationData.fromJson(Map<String, dynamic> json) {
    return TransportationData(
      duration: json['duration'] as String,
      method: json['method'] as String,
      cost: json['cost'] as double?,
    );
  }
}
```

### UI Layout

#### Comparative Table Design

The table should allow users to view multiple plan options side-by-side for easy comparison. Each option is a column.

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Option 1             │  Option 2             │  Option 3               │
│  Total: $4200         │  Total: $3800         │  Total: $5100           │
│  Notes: Cultural...   │  Notes: Adventure...  │  Notes: Luxury...       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Day 1: Explore...    │  Day 1: Mountain...   │  Day 1: City tour...    │
│  [Lodging]            │  [Lodging]            │  [Lodging]              │
│                       │                       │                         │
│  9:00 - 11:30         │  8:00 - 10:00         │  10:00 - 12:00          │
│  Visit temple         │  Hiking trail         │  Museum visit           │
│  🚶 10 min walking    │  🚗 30 min driving    │  🚇 20 min subway       │
│                       │                       │                         │
│  12:00 - 1:00         │  11:00 - 12:30        │  1:00 - 2:30            │
│  Lunch at soba...     │  Picnic lunch         │  Fine dining            │
│                       │                       │                         │
│  ───────────────      │  ───────────────      │  ───────────────        │
│                       │                       │                         │
│  Day 2: Modern...     │  Day 2: Beach...      │  Day 2: Shopping...     │
│  [Lodging]            │  [Lodging]            │  [Lodging]              │
│  ...                  │  ...                  │  ...                    │
│                       │                       │                         │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Implementation Approach

Use a horizontal `SingleChildScrollView` containing a `Row` of option cards. Each card has a fixed width (320px) to ensure consistent sizing.

```dart
Container(
  decoration: BoxDecoration(
    color: Theme.of(context).colorScheme.surfaceVariant,
    borderRadius: BorderRadius.circular(12),
  ),
  padding: const EdgeInsets.all(16),
  child: planOptions.isEmpty
      ? _buildEmptyState()
      : SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: planOptions.asMap().entries.map((entry) {
              final index = entry.key;
              final option = entry.value;
              return Padding(
                padding: EdgeInsets.only(right: index < planOptions.length - 1 ? 16 : 0),
                child: _buildOptionCard(option, index + 1),
              );
            }).toList(),
          ),
        ),
)
```

#### Option Card

Each option is displayed in a card with fixed width (320px) and scrollable content:

```dart
Widget _buildOptionCard(PlanOptionData option, int optionNumber) {
  return Container(
    width: 320,
    decoration: BoxDecoration(
      color: Theme.of(context).colorScheme.surface,
      borderRadius: BorderRadius.circular(12),
      border: Border.all(
        color: Theme.of(context).dividerColor,
        width: 1,
      ),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header with option number and cost
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
              Text(
                'Option $optionNumber',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                'Total: ${option.overallCost}',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
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
        // Days list (scrollable)
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: option.days.length,
            separatorBuilder: (context, index) => const Divider(height: 24),
            itemBuilder: (context, index) {
              return _buildDayCard(option.days[index], index + 1);
            },
          ),
        ),
      ],
    ),
  );
}
```

#### Day Card

Each day within an option card:

```dart
Widget _buildDayCard(DayData day, int dayNumber) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      // Day header
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
            Icon(
              Icons.hotel,
              size: 16,
              color: Theme.of(context).colorScheme.primary,
            ),
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
      // Time blocks
      ...day.blocks.map((block) => _buildTimeBlock(block)),
    ],
  );
}
```

#### Time Block

Each time block within a day:

```dart
Widget _buildTimeBlock(BlockData block) {
  return Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Time
        Text(
          block.time,
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 4),
        // Description
        Text(
          block.description,
          style: Theme.of(context).textTheme.bodyMedium,
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        ),
        // Transportation (if available)
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
              Text(
                '${block.transportation!.duration} · ${block.transportation!.method}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.secondary,
                    ),
              ),
              if (block.transportation!.cost != null) ...[
                const SizedBox(width: 4),
                Text(
                  '· \$${block.transportation!.cost!.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.secondary,
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ],
          ),
        ],
        // POIs (if available)
        if (block.pois != null && block.pois!.isNotEmpty) ...[
          const SizedBox(height: 6),
          Wrap(
            spacing: 4,
            runSpacing: 4,
            children: block.pois!.map((poi) {
              return Chip(
                label: Text(
                  poi.name,
                  style: const TextStyle(fontSize: 11),
                ),
                avatar: Icon(
                  _getPoiIcon(poi.poiType),
                  size: 14,
                ),
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
```

#### Transport Icon Mapping

```dart
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
```

### Empty State
If no plan options are available:
```
┌─────────────────────────────────────┐
│                                     │
│       [Icon: event_available]       │
│                                     │
│     No Trip Options Yet             │
│                                     │
│  Tell the assistant your dates      │
│  and preferences to generate        │
│  personalized itineraries!          │
│                                     │
└─────────────────────────────────────┘
```

### Loading State
While plan options are being generated:
- Show shimmer placeholders for 2-3 option cards
- Same card structure but with animated shimmer effect

---

## Data Flow & Backend Integration

### Backend API Contract

The backend exposes a `/chat` endpoint that accepts user messages and returns structured data.

#### Request

```
POST http://localhost:5000/chat
Content-Type: application/json

{
  "message": "I want to visit Tokyo in April for 3 days"
}
```

#### Response

```json
{
  "intents": [
    {
      "intent_type": "Points_Of_Interest",
      "response_text": "I found some great places in Tokyo!"
    },
    {
      "intent_type": "Schedule_Requirement",
      "response_text": "Got it, 3 days in April."
    }
  ],
  "pois": [
    {
      "name": "Senso-ji Temple",
      "description": "Ancient Buddhist temple in Asakusa",
      "geo_coordinate": {
        "lat": 35.7148,
        "lng": 139.7929
      },
      "poi_type": "tourist_destination",
      "images": {
        "urls": [
          "https://example.com/image1.jpg",
          "https://example.com/image2.jpg"
        ]
      },
      "opening_hours": "6:00 AM - 5:00 PM",
      "address": "2-3-1 Asakusa, Taito City, Tokyo",
      "special_instructions": "Remove shoes before entering",
      "cost": "$5"
    }
  ],
  "requirements": [
    {
      "description": "3 days in April",
      "priority": "must_have"
    },
    {
      "description": "Visit cultural sites",
      "priority": "preferred"
    }
  ],
  "plan": [
    {
      "overall_cost": "$4200",
      "general_notes": "A 3-day cultural tour of Tokyo...",
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
                  "description": "Ancient Buddhist temple",
                  "geo_coordinate": {
                    "lat": 35.7148,
                    "lng": 139.7929
                  }
                }
              ]
            },
            {
              "time": "12:00 PM - 1:00 PM",
              "description": "Lunch at a local soba restaurant",
              "transportation": {
                "duration": "10 minutes",
                "method": "walking"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### State Management Approach

Use a `StatefulWidget` for the home page (`MyHomePage`) with the following state:

```dart
class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _chatController = TextEditingController();
  final List<ChatMessage> _messages = [];
  List<POIData> _pois = [];
  List<RequirementData> _requirements = [];
  List<PlanOptionData> _planOptions = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Add initial system message
    _messages.add(ChatMessage(
      text: 'Hi! Tell me your destination, dates, and preferences.',
      isUser: false,
    ));
  }

  Future<void> _sendMessage(String message) async {
    if (message.trim().isEmpty) return;

    // Add user message
    setState(() {
      _messages.add(ChatMessage(text: message, isUser: true));
      _isLoading = true;
    });

    // Clear input
    _chatController.clear();

    try {
      // Send to backend
      final response = await http.post(
        Uri.parse('http://localhost:5000/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'message': message}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;

        // Extract bot responses from intents
        final intents = data['intents'] as List<dynamic>? ?? [];
        final botResponses = intents
            .map((i) => (i as Map<String, dynamic>)['response_text'] as String?)
            .where((text) => text != null && text.isNotEmpty)
            .join('\n\n');

        setState(() {
          if (botResponses.isNotEmpty) {
            _messages.add(ChatMessage(text: botResponses, isUser: false));
          }

          // Update POIs
          if (data['pois'] != null) {
            final poisJson = data['pois'] as List<dynamic>;
            _pois = poisJson
                .map((p) => POIData.fromJson(p as Map<String, dynamic>))
                .toList();
          }

          // Update Requirements
          if (data['requirements'] != null) {
            final reqsJson = data['requirements'] as List<dynamic>;
            _requirements = reqsJson
                .map((r) => RequirementData.fromJson(r as Map<String, dynamic>))
                .toList();
          }

          // Update Plan Options
          if (data['plan'] != null) {
            final plansJson = data['plan'] as List<dynamic>;
            _planOptions = plansJson
                .map((p) => PlanOptionData.fromJson(p as Map<String, dynamic>))
                .toList();
          }

          _isLoading = false;
        });
      } else {
        setState(() {
          _messages.add(ChatMessage(
            text: 'Sorry, I encountered an error. Please try again.',
            isUser: false,
          ));
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: 'Network error. Please check your connection.',
          isUser: false,
        ));
        _isLoading = false;
      });
    }
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
          final Widget mainPanel = MainViewPanel(
            pois: _pois,
            requirements: _requirements,
            planOptions: _planOptions,
          );
          final Widget chatPanel = ChatViewPanel(
            controller: _chatController,
            messages: _messages,
            onSendMessage: _sendMessage,
            isLoading: _isLoading,
          );

          if (isWide) {
            return Row(
              children: [
                Expanded(flex: 3, child: mainPanel),
                Container(
                  width: 1,
                  color: Theme.of(context).dividerColor,
                ),
                Expanded(flex: 2, child: chatPanel),
              ],
            );
          }

          return Column(
            children: [
              Expanded(child: mainPanel),
              Container(
                height: 1,
                color: Theme.of(context).dividerColor,
              ),
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

### Data Accumulation Strategy

The frontend should **accumulate** data across multiple chat interactions:
- When new POIs are received, **append** them to the existing list (avoid duplicates by name)
- When new requirements are received, **append** them to the existing list (avoid duplicates by description)
- When new plan options are received, **replace** the existing list (plans are regenerated based on all requirements)

This means users can incrementally build their trip by chatting, and all data remains visible.

---

## Responsive Behavior

### Breakpoint: 900px

#### Width >= 900px (Desktop/Wide)
- Side-by-side layout (Row)
- Left section: 60% width
- Right section: 40% width
- POI Gallery: 4-5 columns depending on total width
- Trip Options: Cards side-by-side with horizontal scroll

#### Width < 900px (Mobile/Narrow)
- Stacked layout (Column)
- Top section (Main Panel): 55% height
- Bottom section (Chat Panel): 45% height
- POI Gallery: 2-3 columns depending on width
- Trip Options: Cards still side-by-side with horizontal scroll (maintains 320px width)

### Additional Responsive Considerations

#### Mobile-Specific Behavior
- POI Gallery: On mobile, use `InkWell` with `onTap` instead of `MouseRegion` for hover overlay
- Trip Options: Ensure horizontal scroll is clearly indicated (e.g., show partial card on right edge)
- Chat Input: Reduce padding in narrow layouts

#### Tablet (600px - 900px)
- POI Gallery: 3 columns
- All other behavior follows mobile stacked layout

---

## State Management

### Recommended Approach: setState + StatefulWidget

For the pre-MVP phase, use Flutter's built-in `setState` with a `StatefulWidget` for the home page. This is sufficient for the current scope and avoids introducing additional dependencies.

### State Location
All shared state lives in `_MyHomePageState`:
- Chat messages list
- POIs list
- Requirements list
- Plan options list
- Loading flag

### Data Flow
1. User sends message via `ChatViewPanel`
2. Callback triggers `_sendMessage()` in `_MyHomePageState`
3. HTTP request sent to backend
4. Response parsed and state updated via `setState()`
5. All child widgets (`MainViewPanel`, `ChatViewPanel`) rebuild with new data

### Future Enhancement (Post-MVP)
If the app grows in complexity, consider migrating to:
- **Provider** (for shared state across multiple screens)
- **Riverpod** (more robust dependency injection)
- **Bloc** (for complex business logic and event-driven architecture)

---

## Component Hierarchy

### File Structure

```
frontend/lib/
├── main.dart                           # Root app + MyHomePage (stateful)
├── models/
│   ├── chat_message.dart               # ChatMessage model
│   ├── poi_data.dart                   # POIData model
│   ├── requirement_data.dart           # RequirementData model
│   ├── plan_option_data.dart           # PlanOptionData, DayData, BlockData, TransportationData
├── services/
│   └── api_service.dart                # HTTP client for /chat endpoint
├── widgets/
│   ├── chat_view_panel.dart            # Chat UI (modified)
│   ├── chat_bubble.dart                # Individual chat message (unchanged)
│   ├── main_view_panel.dart            # Trip planner container (modified)
│   ├── poi_gallery_section.dart        # POI photo grid with hover overlays
│   ├── poi_photo_tile.dart             # Individual photo tile with overlay
│   ├── requirements_section.dart       # Requirements chips display
│   ├── trip_options_section.dart       # Comparative table of plans
│   ├── option_card.dart                # Single plan option card
│   ├── day_card.dart                   # Day within a plan option
│   └── time_block.dart                 # Time block within a day
└── utils/
    └── icon_helpers.dart               # Icon mapping functions
```

### Widget Tree (High-Level)

```
MyApp (StatelessWidget)
└── MaterialApp
    └── MyHomePage (StatefulWidget)
        └── Scaffold
            ├── AppBar
            └── LayoutBuilder
                └── Row (if wide) | Column (if narrow)
                    ├── MainViewPanel (StatelessWidget)
                    │   └── Column
                    │       ├── Header
                    │       └── Expanded Column
                    │           ├── POIGallerySection (StatefulWidget for hover)
                    │           ├── RequirementsSection (StatelessWidget)
                    │           └── TripOptionsSection (StatelessWidget)
                    └── ChatViewPanel (StatefulWidget)
                        └── Column
                            ├── Header
                            ├── ListView (messages)
                            └── TextField + Button
```

---

## Visual Design Guidelines

### Color Palette
Use Material 3 theming with `ColorScheme.fromSeed`:
- **Primary**: Deep purple (as currently defined)
- **Surface**: Light background for main content areas
- **SurfaceVariant**: Slightly darker for sections/containers
- **PrimaryContainer**: Highlighted areas (e.g., option card headers)

### Typography
Use theme-defined text styles:
- **headlineMedium**: Section titles (Trip Planner)
- **titleLarge**: Subsection headers (Chat Assistant, POI Gallery)
- **titleMedium**: Day highlights, option titles
- **bodyLarge**: Descriptive text
- **bodyMedium**: Standard body text
- **bodySmall**: Metadata (time, transportation details)
- **labelLarge**: Labels (time in blocks)

### Spacing
- Section padding: 24px
- Inter-section spacing: 16px
- Card padding: 16px
- Chip spacing: 8px
- Grid item spacing: 8px

### Elevation & Shadows
- Photo tiles: Subtle elevation (elevation: 2)
- Option cards: Border (1px) instead of elevation for cleaner look
- Hover overlays: No elevation, use opacity for depth

### Animations
- Hover overlay: `AnimatedOpacity` with 200ms duration
- Chat scroll: `animateTo()` with 300ms duration
- Loading states: Shimmer animation with 1500ms cycle

---

## Edge Cases

### 1. Empty States
All three sub-sections must handle empty data gracefully:
- **POI Gallery**: Show centered message with icon
- **Requirements**: Show centered message with icon
- **Trip Options**: Show centered message with icon

Each empty state should encourage user action (e.g., "Chat with the assistant...").

### 2. Loading States
- **Chat**: Show "Analyzing your request..." as a system message bubble
- **POI Gallery**: Show shimmer grid (8 placeholder tiles)
- **Trip Options**: Show shimmer cards (2-3 placeholder cards)

### 3. Error States

#### Network Error
If the HTTP request fails:
- Show error message in chat: "Network error. Please check your connection."
- Keep existing data in left panel (don't clear it)
- User can retry by sending another message

#### Backend Error (4xx/5xx)
- Show error message in chat: "Sorry, I encountered an error. Please try again."
- Keep existing data in left panel

#### Malformed Response
If the response doesn't match expected schema:
- Log error to console
- Show generic error message in chat
- Don't crash the app

### 4. Large Datasets

#### Many POIs (50+ POIs with 5+ images each = 250+ photos)
- Grid should handle large lists efficiently via `GridView.builder`
- Images loaded lazily with `Image.network` (built-in lazy loading)
- Consider pagination or "Load More" button in future iterations

#### Long Plans (10+ days, 10+ blocks per day)
- Each option card is scrollable independently
- Horizontal scroll for multiple options works regardless of content length

#### Long Requirement Descriptions
- Use `maxLines` and `TextOverflow.ellipsis` to prevent overflow
- Consider tooltip on hover for full text (future enhancement)

### 5. Image Loading Failures
- Use `errorBuilder` in `Image.network` to show placeholder icon
- Placeholder: Gray container with `Icons.broken_image` centered

```dart
Image.network(
  imageUrl,
  fit: BoxFit.cover,
  loadingBuilder: (context, child, loadingProgress) {
    if (loadingProgress == null) return child;
    return Center(
      child: CircularProgressIndicator(
        value: loadingProgress.expectedTotalBytes != null
            ? loadingProgress.cumulatedBytesLoaded / loadingProgress.expectedTotalBytes!
            : null,
      ),
    );
  },
  errorBuilder: (context, error, stackTrace) {
    return Container(
      color: Colors.grey.shade300,
      child: Center(
        child: Icon(
          Icons.broken_image,
          size: 48,
          color: Colors.grey.shade600,
        ),
      ),
    );
  },
)
```

### 6. No Images for POI
If a POI has an empty `images.urls` list:
- Don't display any tiles for that POI in the gallery
- The POI will still appear in plan options (as chips in time blocks)

### 7. Missing Optional Fields
- **Address**: Don't show if null
- **Opening Hours**: Don't show if null
- **Special Instructions**: Don't show if null (could add in future iterations)
- **Cost**: Don't show if null or empty string
- **Lodging**: Don't show icon/text if null
- **Transportation**: Don't show if null
- **POIs in Blocks**: Don't show chips if null or empty

### 8. Very Long Text
All text fields should have `maxLines` and `TextOverflow.ellipsis`:
- POI descriptions: 3 lines
- Requirement descriptions: 2 lines (in chips)
- Day highlights: 2 lines
- Block descriptions: 3 lines
- General notes (option header): 2 lines

### 9. Duplicate Data
When accumulating POIs and requirements:
- Check for duplicates before adding to state
- For POIs: Compare by `name` (case-insensitive)
- For Requirements: Compare by `description` (case-insensitive)

```dart
// Example deduplication for POIs
void _updatePOIs(List<POIData> newPOIs) {
  final existingNames = _pois.map((p) => p.name.toLowerCase()).toSet();
  final uniqueNewPOIs = newPOIs.where((p) => !existingNames.contains(p.name.toLowerCase())).toList();
  setState(() {
    _pois.addAll(uniqueNewPOIs);
  });
}
```

### 10. Rapid Message Sending
- Disable send button while `_isLoading` is true
- Prevent user from sending multiple requests simultaneously

```dart
FilledButton(
  onPressed: _isLoading ? null : () {
    final text = controller.text;
    if (text.trim().isNotEmpty) {
      widget.onSendMessage(text);
    }
  },
  child: const Icon(Icons.send),
)
```

### 11. Backend Not Running
If backend is not reachable:
- Show network error message (handled by error case)
- Consider adding a connection status indicator in future iterations

### 12. Mobile Hover Behavior
On mobile devices, `MouseRegion` won't work. Use `InkWell` with `onTap` to toggle overlay visibility:
- Tap once to show overlay
- Tap again (or tap elsewhere) to hide overlay
- Store tapped tile index in state

```dart
InkWell(
  onTap: () {
    setState(() {
      _tappedIndex = _tappedIndex == index ? null : index;
    });
  },
  child: Stack(
    children: [
      Image.network(url),
      AnimatedOpacity(
        opacity: _tappedIndex == index ? 1.0 : 0.0,
        duration: const Duration(milliseconds: 200),
        child: _buildOverlay(poi),
      ),
    ],
  ),
)
```

---

## Implementation Sequence

### Phase 1: Foundation (Blockers removed, data models ready)
1. Create data models (`models/` directory)
   - `chat_message.dart`
   - `poi_data.dart`
   - `requirement_data.dart`
   - `plan_option_data.dart`
2. Create API service (`services/api_service.dart`)
   - HTTP client with `/chat` endpoint method
3. Modify `_MyHomePageState` in `main.dart`
   - Add state variables
   - Implement `_sendMessage()` method
   - Wire up API calls

### Phase 2: Chat UI Enhancement
4. Modify `ChatViewPanel` to accept messages and callbacks
5. Add loading state to chat (system message bubble)
6. Implement auto-scroll on new message
7. Test chat interaction end-to-end

### Phase 3: Main View Panel Restructure
8. Create section container widgets
   - `poi_gallery_section.dart` (with empty state)
   - `requirements_section.dart` (with empty state)
   - `trip_options_section.dart` (with empty state)
9. Modify `MainViewPanel` to use 3-section layout
10. Test responsive behavior (900px breakpoint)

### Phase 4: POI Gallery Implementation
11. Create `poi_photo_tile.dart` with hover overlay (desktop)
12. Add mobile tap behavior (toggle overlay on tap)
13. Implement grid layout with adaptive columns
14. Add image loading/error states
15. Test with real backend data

### Phase 5: Requirements Display
16. Implement chip layout with `Wrap`
17. Add color-coding by priority
18. Add priority icons
19. Test with various requirement counts

### Phase 6: Trip Options Table
20. Create `option_card.dart` with header and scrollable days
21. Create `day_card.dart` with highlight and lodging
22. Create `time_block.dart` with transportation and POIs
23. Implement horizontal scroll for multiple options
24. Add transportation and POI icons
25. Test with complex multi-day plans

### Phase 7: Polish & Edge Cases
26. Add loading states (shimmer placeholders)
27. Implement deduplication logic for POIs and requirements
28. Add empty states for all sections
29. Implement error handling for all network calls
30. Test all responsive breakpoints
31. Performance testing with large datasets

### Phase 8: Final Testing & Documentation
32. End-to-end testing with backend
33. Cross-browser testing (Chrome, Safari, Firefox)
34. Mobile device testing (iOS, Android)
35. Update README with usage instructions

---

## Dependencies

### Required Packages
Add to `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0                # For HTTP requests

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
```

### Optional (Future Enhancements)
- `shimmer: ^3.0.0` - For loading shimmer effects
- `cached_network_image: ^3.3.0` - For better image caching
- `flutter_staggered_grid_view: ^0.7.0` - For Pinterest-style grid (if desired)

---

## Open Questions

1. **POI Deduplication**: Should POIs with the same name but different types (e.g., "Central Park" as restaurant vs tourist_destination) be considered duplicates?
   - **Recommendation**: Consider duplicates if name matches exactly (case-insensitive), regardless of type.

2. **Plan Regeneration**: When should plan options be regenerated? On every new requirement, or only when user explicitly asks?
   - **Recommendation**: Backend decides. Frontend just displays whatever plan array is returned.

3. **POI Image Selection**: If a POI has multiple images, should the gallery show all of them, or just the first one?
   - **Specification**: Show ALL images for ALL POIs (as stated in requirements).

4. **Mobile Overlay Behavior**: On mobile, should tapping a photo open a full-screen modal with POI details, or just toggle the overlay?
   - **Recommendation**: Start with overlay toggle (simpler). Full-screen modal is a nice-to-have for future iterations.

5. **Plan Selection**: Should users be able to "select" a plan option, or are they purely for comparison?
   - **Recommendation**: Purely for comparison in MVP. Selection/booking is post-MVP.

6. **Offline Support**: Should the app cache data for offline viewing?
   - **Recommendation**: Not for MVP. This requires persistence layer which doesn't exist yet.

7. **Real-time Updates**: Should the UI update in real-time as the backend generates results (e.g., POIs appear incrementally)?
   - **Recommendation**: Not for MVP. Would require WebSocket or polling, adding complexity.

---

## Acceptance Criteria

A successful implementation meets these criteria:

### Functional
- [ ] User can send messages via chat and receive responses
- [ ] POIs are displayed in a photo grid with hover/tap overlays showing details
- [ ] Requirements are displayed as color-coded chips
- [ ] Trip options are displayed in a comparative table with scrollable days
- [ ] All data accumulates across multiple chat interactions
- [ ] Layout responds correctly at 900px breakpoint (side-by-side vs stacked)
- [ ] Loading states are shown during backend requests
- [ ] Empty states are shown when no data is available
- [ ] Error states are handled gracefully (network errors, backend errors)

### Visual
- [ ] Consistent Material 3 theming throughout
- [ ] Proper spacing and alignment (no overlapping elements)
- [ ] Text truncates gracefully with ellipsis (no overflow errors)
- [ ] Images load with placeholders and handle errors
- [ ] Hover/tap overlays animate smoothly
- [ ] Chat auto-scrolls to latest message

### Technical
- [ ] No console errors or warnings
- [ ] Handles large datasets (50+ POIs, 10+ day plans)
- [ ] HTTP requests use proper error handling
- [ ] State management is clear and maintainable
- [ ] Code follows Dart style guidelines

### Responsive
- [ ] Works on desktop (1920px+)
- [ ] Works on laptop (1366px - 1920px)
- [ ] Works on tablet (768px - 1024px)
- [ ] Works on mobile (375px - 768px)
- [ ] Horizontal scroll works on trip options table

---

## Notes for Implementation

1. **Start with Structure**: Build the component hierarchy first with placeholder data before wiring up the backend.

2. **Test Incrementally**: After each phase, test with both empty and populated data to ensure empty/loading states work.

3. **Use Theme Consistently**: Always reference `Theme.of(context)` for colors, never hardcode colors (except in specific cases like overlay opacity).

4. **Keep Widgets Small**: Each widget file should be focused on a single responsibility. If a widget gets too large (>200 lines), consider splitting it.

5. **Data Validation**: Always validate JSON data in `fromJson()` factories. Use null-aware operators and provide sensible defaults.

6. **Performance**: Use `ListView.builder` and `GridView.builder` instead of `ListView()` and `GridView()` for better performance with large lists.

7. **Accessibility**: Add semantic labels for icons and images where appropriate (future enhancement).

8. **Testing**: Write widget tests for each new component (future enhancement, not required for MVP).

---

## File Paths Reference

All file paths referenced in this spec are absolute:

- **Backend Data Models**:
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/backend/app/POI/POIModel.py`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/backend/app/Planner/RequirementModel.py`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/backend/app/Planner/PlanOptionModel.py`

- **Frontend Existing Widgets**:
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/main.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/chat_view_panel.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/main_view_panel.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/chat_bubble.dart`

- **Frontend New Files** (to be created):
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/models/chat_message.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/models/poi_data.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/models/requirement_data.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/models/plan_option_data.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/services/api_service.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/poi_gallery_section.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/poi_photo_tile.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/requirements_section.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/trip_options_section.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/option_card.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/day_card.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/widgets/time_block.dart`
  - `/Users/edy/Desktop/Invest/Code/TravelPlanner/frontend/lib/utils/icon_helpers.dart`

---

**End of Design Specification**
