# TravelPlanner

A starter workspace for a trip planner app focused on long, highly customized itineraries.

## Repository layout
- `frontend/`: Static web prototype (future Flutter app).
- `backend/`: FastAPI service scaffold.
- `docs/`: Architecture notes and planning docs.

## Local development

### Frontend (static prototype)
```bash
cd frontend
python -m http.server 5173
```
Then open http://localhost:5173.

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Health check: http://localhost:8000/health

## What’s next
- Replace the static frontend with a Flutter Web app.
- Connect the UI sections to real backend endpoints.
- Add persistence for trip plans and option comparison.

See `docs/architecture.md` for the current high-level architecture draft.
