# Trip Planner Architecture (Draft)

## Goals
- Support long, highly customized trips with a flexible planning workflow.
- Combine chat-based idea capture, structured prioritization, and visual selection.
- Produce a polished itinerary output for sharing or export.

## High-level components
- **Frontend (Flutter Web + iPad app)**
  - Primary UI for travelers and planners.
  - Modules: chat workspace, requirement prioritization, option comparison, visual selection, and itinerary export.
  - Future: use Flutter Web for web deployment and iPad packaging.
- **Backend (Python API)**
  - Manages trip data, options, and chat context.
  - Provides endpoints for chat/idea intake, itinerary generation, and structured data storage.
- **Data layer**
  - Short term: SQLite/Postgres for trips, preferences, and option metadata.
  - Long term: vector store for retrieval and chat context.

## Initial data model (draft)
- Trip
  - id, title, date range, travel pace, preferences
- Requirement
  - id, trip_id, label, priority (must-have/nice-to-have)
- Option
  - id, trip_id, type (destination/restaurant/lodging), score, notes
- ItineraryItem
  - id, trip_id, day, description, location

## Next iterations
1. Hook up frontend forms to backend endpoints.
2. Add persistent storage.
3. Integrate an AI workflow for idea extraction and itinerary formatting.
