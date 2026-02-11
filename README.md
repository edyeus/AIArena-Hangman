# TravelPlanner

A trip planner app for long, highly customized itineraries. Chat with an AI assistant to describe your destination, dates, and preferences — the app discovers points of interest, captures your requirements, and generates multiple itinerary options with an interactive map view.

## Prerequisites

- **Flutter** SDK ^3.5.3 — [install guide](https://docs.flutter.dev/get-started/install)
- **Python** 3.10+ — for the backend
- **Azure AI** credentials — the backend uses Azure AI agents for intent analysis, POI discovery, and itinerary planning

## Repository Layout

```
frontend/   Flutter app (Dart) — chat UI, POI gallery, trip options, interactive map
backend/    Flask API (Python) — orchestrator, POI agent, planner agent
```

## Getting Started

### Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
pip install flask flask-cors azure-ai-projects azure-identity

# Run the server (port 5000)
python app/app.py
```

Verify it's running:

```bash
curl http://127.0.0.1:5000/health
# {"status": "ok"}
```

### Frontend

```bash
cd frontend

# Install dependencies
flutter pub get

# Run on Chrome (or any target)
flutter run -d chrome
```

The frontend connects to `ws://127.0.0.1:5000/ws/chat` for real-time streaming and falls back to `POST /chat` for one-shot requests. Make sure the backend is running first.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send `{"message": "..."}` for intent analysis |
| `WebSocket` | `/ws/chat` | Streaming chat — sends progressive `intents`, `pois`, `requirements`, `plan`, and `done` messages |
| `POST` | `/testpoi` | POI discovery (test endpoint) |
| `POST` | `/testingplanner` | Full planning pipeline (test endpoint) |

## Architecture

```
Flutter UI (chat + main view + map)
    |
    | WebSocket / HTTP
    v
Flask API (backend/app/app.py)
    |-- Orchestrator   — classifies user input into structured intents
    |-- POI module      — discovers POIs via Azure AI agent, fetches images (Flickr, Google Places)
    |-- Planner module  — generates multiple itinerary options from POIs + requirements
```

### Frontend (`frontend/lib/`)

- **`main.dart`** — Root widget, Material 3 theming, responsive layout (side-by-side at 900px+, stacked below), WebSocket state management
- **`models/`** — Data models (`POI`, `PlanOption`, `Requirement`, `ChatMessage`) with JSON serialization
- **`widgets/`** — `ChatViewPanel` (chat interface), `MainViewPanel` (content area), `PoiGallerySection`, `RequirementsSection`, `TripOptionsSection`, `MapSection` (interactive OpenStreetMap with POI markers and route polylines)

### Backend (`backend/app/`)

- **`Orchestrator/`** — Intent classification using Azure AI with JSON output schema
- **`POI/`** — POI discovery (`POIAgent.py`), data models (`POIModel.py`), image fetching (`ImageFetcher.py`)
- **`Planner/`** — Itinerary generation (`Planner.py`), plan model (`PlanOptionModel.py` — options, days, time blocks, transportation), requirement model (`RequirementModel.py` with priorities: MUST_HAVE, PREFERRED, AVOID)

## Useful Commands

```bash
# Frontend
cd frontend
flutter analyze           # Lint / static analysis
flutter test              # Run all tests
flutter build web         # Production web build

# Backend
cd backend
python app/app.py         # Start Flask dev server on :5000
```

## Current Status

Pre-MVP. The frontend UI is functional with chat, POI gallery, trip options with selection, and an interactive map. The backend AI pipeline (Orchestrator → POI → Planner) works but requires Azure credentials. No persistence layer exists yet.
