# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Trip planner app for long, highly customized itineraries. Combines chat-based idea capture with AI-powered POI discovery and itinerary scheduling.

- **Frontend:** Flutter (Dart, SDK ^3.5.3) — targets web, iOS, Android, macOS, Windows, Linux
- **Backend:** Flask (Python) with Azure AI agent orchestration — despite README/requirements.txt referencing FastAPI, the actual server is Flask

## Commands

### Frontend (in `frontend/`)
```bash
flutter run -d chrome          # Run web dev server
flutter test                   # Run all tests
flutter test test/widget_test.dart  # Run a single test file
flutter analyze                # Lint/static analysis
flutter build web              # Production web build
```

### Backend (in `backend/`)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Also needs: pip install flask flask-cors azure-ai-projects azure-identity
python app/app.py              # Runs Flask on port 5000
```

Backend endpoints:
- `GET /health` — health check
- `POST /chat` — send `{"message": "..."}` for intent analysis
- `POST /testpoi` — POI discovery (test endpoint)
- `POST /testingplanner` — full planning pipeline (test endpoint)

## Architecture

```
Flutter UI (chat panel + main view)
    ↓ HTTP
Flask API (backend/app/app.py)
    ├── Orchestrator — analyzes user chat input into structured intents
    │   (intents: Points_Of_Interest, Schedule_Requirement, Schedule_Option, General_Response, Not_Relevant)
    ├── POI module — discovers points of interest via Azure AI agent + fetches images (Flickr, Google Places)
    └── Planner module — combines POIs + requirements → generates multiple itinerary options via Azure AI Scheduler agent
```

### Backend modules (`backend/app/`)

- **`Orchestrator/`** — Intent classification from raw chat. Uses Azure AI agent with strict JSON output schema and retry logic (MAX_ATTEMPTS=2).
- **`POI/`** — POI discovery (`POIAgent.py`), data models (`POIModel.py`), and image fetching (`ImageFetcher.py` — Flickr/Google Places APIs). Missing `__init__.py`.
- **`Planner/`** — Itinerary generation (`Planner.py`), complex nested plan model (`PlanOptionModel.py` — options → days → time blocks → transportation/POIs), and requirement model (`RequirementModel.py` with Priority enum: MUST_HAVE, PREFERRED, AVOID).

### Frontend structure (`frontend/lib/`)

- **`main.dart`** — Root widget, Material 3 theming, responsive layout (side-by-side ≥900px, stacked below).
- **`widgets/`** — `MainViewPanel` (map/itinerary area), `ChatViewPanel` (chat interface), `ChatBubble` (message component). Currently static/placeholder — not yet connected to backend.

### Data model conventions (Python)

All models use `@dataclass` with consistent patterns: `to_dict()`/`to_list()` for serialization, `from_json()` for deserialization, `validate_json()` for validation. Cost fields stored as strings for currency flexibility.

## Current State

Pre-MVP. The frontend UI is scaffold-only with hardcoded placeholder data. The backend AI pipeline (Orchestrator → POI → Planner) works but requires Azure credentials. Frontend-backend integration is not yet wired up. No persistence layer exists yet.
