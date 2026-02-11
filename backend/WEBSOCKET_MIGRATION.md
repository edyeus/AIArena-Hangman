# WebSocket Migration for /chat Endpoint

This document describes the WebSocket implementation that enables progressive streaming updates for the chat endpoint.

## Overview

The chat endpoint now supports two modes:
1. **REST API** (existing): `POST /chat` - returns complete response after all processing
2. **WebSocket** (new): `ws://host/ws/chat` - streams progressive updates as processing happens

## Architecture

### Message Flow

```
Client connects to ws://127.0.0.1:5000/ws/chat
    ↓
Client sends: {"message": "...", "pois": [], "requirements": [], "plan": []}
    ↓
Server processes and yields progressive updates:
    1. {"type": "intents", "data": [...]}        ← Classified intents
    2. {"type": "pois", "data": [...]}           ← POI discovery results
    3. {"type": "requirements", "data": [...]}   ← Updated requirements
    4. {"type": "plan", "data": [...]}           ← Generated itinerary options
    5. {"type": "done"}                          ← Processing complete
```

### Error Handling

If an error occurs at any stage:
```json
{"type": "error", "message": "description of error"}
```

## Implementation Details

### Files Modified

1. **`backend/requirements.txt`**
   - Added `flask-sock` dependency

2. **`backend/app/app.py`**
   - Imported `flask_sock.Sock` and `analyze_intents_stream`
   - Created `Sock(app)` instance
   - Added `@sock.route('/ws/chat')` WebSocket handler
   - REST endpoint `/chat` remains unchanged

3. **`backend/app/Orchestrator/Orchestrator.py`**
   - Added `analyze_intents_stream()` generator function
   - Yields progressive updates as each stage completes
   - Wraps all logic in try/except to prevent server crashes
   - Maintains same business logic as `analyze_intents()`

4. **`backend/app/Orchestrator/__init__.py`**
   - Exported `analyze_intents_stream` alongside `analyze_intents`

## Update Types

| Type | Description | Data Format |
|------|-------------|-------------|
| `intents` | Classified user intents | Array of `{intent, action, value}` |
| `pois` | Points of interest | Array of POI objects (from `POIModel.to_list()`) |
| `requirements` | Trip requirements | Array of `{description, priority}` |
| `plan` | Itinerary options | Array of plan options (from `PlanOptionModel.to_list()`) |
| `done` | Processing complete | No data field |
| `error` | Error occurred | `{message: "error description"}` |

## Client Implementation

### Python Example

See `backend/ws_chat_example.py` for a complete Python client using `websocket-client`.

```bash
pip install websocket-client
python ws_chat_example.py
```

### Browser Example

Open `backend/ws_chat_client.html` in a browser (after starting the Flask server).

### JavaScript/TypeScript (for Flutter Web or React)

```javascript
const ws = new WebSocket('ws://127.0.0.1:5000/ws/chat');

ws.onopen = () => {
  const payload = {
    message: "plan a 3 day trip to Tokyo",
    pois: [],
    requirements: [],
    plan: []
  };
  ws.send(JSON.stringify(payload));
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);

  switch (update.type) {
    case 'intents':
      console.log('Intents:', update.data);
      break;
    case 'pois':
      console.log('POIs:', update.data);
      break;
    case 'requirements':
      console.log('Requirements:', update.data);
      break;
    case 'plan':
      console.log('Plan:', update.data);
      break;
    case 'done':
      console.log('Processing complete');
      ws.close();
      break;
    case 'error':
      console.error('Error:', update.message);
      ws.close();
      break;
  }
};
```

## Testing

### Start the Flask Server

```bash
cd backend
source .venv/bin/activate  # If using venv
pip install flask-sock     # Install new dependency
python app/app.py
```

Server runs on `http://127.0.0.1:5000`

### Test with Python Client

```bash
python ws_chat_example.py
```

### Test with Browser Client

1. Open `ws_chat_client.html` in a browser
2. Enter a message (default: "plan a 3 day trip to Tokyo and Kyoto")
3. Click "Send Message"
4. Watch progressive updates appear in real-time

### Test with curl (REST endpoint still works)

```bash
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "plan a 3 day trip to Tokyo", "pois": [], "requirements": [], "plan": []}'
```

## Performance Characteristics

### REST (original)
- Single request-response cycle
- Client waits for entire pipeline to complete
- Response time: 10-30 seconds (depends on Azure AI latency)

### WebSocket (new)
- Progressive streaming
- Client receives updates as each stage completes:
  - Intents: ~2-3 seconds
  - POIs: ~5-10 seconds (fetches from APIs)
  - Requirements: instant (after POIs)
  - Plan: ~5-10 seconds (Azure AI planning agent)
- Better UX: user sees progress instead of waiting

## Edge Cases Handled

1. **Validation Failure**: After MAX_ATTEMPTS (2) retries, yields error message
2. **No Actionable Intents**: Yields existing state unchanged, then done
3. **Exception During Processing**: Yields error message with exception details
4. **Malformed Client Message**: Yields error about invalid JSON
5. **Missing Message Field**: Yields error about required field

## Future Enhancements

1. **Cancellation**: Add ability for client to cancel in-flight requests
2. **Progress Percentages**: Yield `{"type": "progress", "percent": 50}`
3. **Partial POI Updates**: Stream each POI as it's discovered (instead of batch)
4. **Reconnection**: Handle WebSocket disconnects with auto-reconnect logic
5. **Authentication**: Add WebSocket authentication/authorization

## Backward Compatibility

The existing REST endpoint `POST /chat` remains fully functional. Clients can choose:
- REST for simple request-response patterns
- WebSocket for progressive streaming and better UX

No breaking changes to existing integrations.
