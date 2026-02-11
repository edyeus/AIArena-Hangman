"""
WebSocket Chat Client Example

This script demonstrates how to connect to the /ws/chat WebSocket endpoint
and receive progressive updates.

Install dependencies:
    pip install websocket-client

Run the Flask server first:
    cd backend
    python app/app.py

Then run this client:
    python ws_chat_example.py
"""

import json
import websocket


def on_message(ws, message):
    """Handle incoming messages from the WebSocket."""
    data = json.loads(message)
    msg_type = data.get("type")

    if msg_type == "intents":
        print(f"\n[INTENTS RECEIVED]")
        for intent in data.get("data", []):
            print(f"  - {intent.get('intent')}: {intent.get('action')} '{intent.get('value')}'")

    elif msg_type == "pois":
        pois = data.get("data", [])
        print(f"\n[POIs RECEIVED] ({len(pois)} total)")
        for poi in pois[:3]:  # Show first 3
            print(f"  - {poi.get('name')}")
        if len(pois) > 3:
            print(f"  ... and {len(pois) - 3} more")

    elif msg_type == "requirements":
        reqs = data.get("data", [])
        print(f"\n[REQUIREMENTS RECEIVED] ({len(reqs)} total)")
        for req in reqs:
            print(f"  - {req.get('description')} [{req.get('priority')}]")

    elif msg_type == "plan":
        plan = data.get("data", [])
        print(f"\n[PLAN RECEIVED] ({len(plan)} options)")
        for i, option in enumerate(plan, 1):
            print(f"  Option {i}: {len(option.get('days', []))} days")

    elif msg_type == "done":
        print(f"\n[DONE] Processing complete!")
        ws.close()

    elif msg_type == "error":
        print(f"\n[ERROR] {data.get('message')}")
        ws.close()

    else:
        print(f"\n[UNKNOWN MESSAGE TYPE] {msg_type}")


def on_error(ws, error):
    """Handle WebSocket errors."""
    print(f"[WebSocket Error] {error}")


def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket connection close."""
    print(f"\n[Connection Closed] {close_status_code}: {close_msg}")


def on_open(ws):
    """Send a message when the WebSocket connection opens."""
    print("[Connected to WebSocket]")

    # Example message
    message = {
        "message": "plan a 3 day trip to Tokyo and Kyoto",
        "pois": [],
        "requirements": [],
        "plan": []
    }

    print(f"\n[Sending] {message['message']}")
    ws.send(json.dumps(message))


if __name__ == "__main__":
    # WebSocket URL for local Flask server
    ws_url = "ws://127.0.0.1:5000/ws/chat"

    # Create WebSocket connection with handlers
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Run forever (will close on "done" or "error" message)
    ws.run_forever()
