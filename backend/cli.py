#!/usr/bin/env python3
"""Interactive REPL for testing the TravelPlanner backend over WebSocket."""

import argparse
import json
import sys
import urllib.request
import urllib.error

try:
    import readline  # noqa: F401 — enables arrow-key history in input()
except ImportError:
    pass

import websocket


# ---------------------------------------------------------------------------
# ANSI colors (no third-party dependency)
# ---------------------------------------------------------------------------
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


# ---------------------------------------------------------------------------
# Conversation state — accumulates across turns
# ---------------------------------------------------------------------------
class ConversationState:
    def __init__(self):
        self.pois: list = []
        self.requirements: list = []
        self.plan: list = []

    def reset(self):
        self.pois = []
        self.requirements = []
        self.plan = []

    def summary(self) -> str:
        lines = []
        lines.append(f"{Color.BOLD}POIs{Color.RESET}: {len(self.pois)}")
        for poi in self.pois:
            name = poi.get("name", "?")
            poi_type = poi.get("poi_type", "")
            lines.append(f"  - {name} ({poi_type})")

        lines.append(f"{Color.BOLD}Requirements{Color.RESET}: {len(self.requirements)}")
        for req in self.requirements:
            desc = req.get("description", "?")
            priority = req.get("priority", "")
            lines.append(f"  - {desc} [{priority}]")

        lines.append(f"{Color.BOLD}Plan options{Color.RESET}: {len(self.plan)}")
        for i, option in enumerate(self.plan, 1):
            days = option.get("days", [])
            lines.append(f"  Option {i}: {len(days)} day(s)")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
def health_check(base_url: str) -> bool:
    url = f"{base_url}/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "ok":
                print(f"{Color.GREEN}Health check passed{Color.RESET} ({url})")
                return True
            print(f"{Color.YELLOW}Health check unexpected response:{Color.RESET} {data}")
            return False
    except urllib.error.URLError as exc:
        print(f"{Color.RED}Health check failed{Color.RESET} ({url}): {exc.reason}")
        return False
    except Exception as exc:
        print(f"{Color.RED}Health check failed{Color.RESET} ({url}): {exc}")
        return False


# ---------------------------------------------------------------------------
# Display helpers — one per message type
# ---------------------------------------------------------------------------
def display_intents(data: list):
    print(f"\n{Color.CYAN}{Color.BOLD}[Intents]{Color.RESET}")
    for intent in data:
        kind = intent.get("intent", "?")
        action = intent.get("action", "?")
        value = intent.get("value", "")
        print(f"  {Color.CYAN}{kind}{Color.RESET} ({action}): {value}")


def display_pois(data: list):
    count = len(data)
    print(f"\n{Color.GREEN}{Color.BOLD}[POIs]{Color.RESET} ({count} total)")
    for poi in data:
        name = poi.get("name", "?")
        desc = poi.get("description", "")
        addr = poi.get("address", "")
        cost = poi.get("cost", "")
        hours = poi.get("opening_hours", "")
        tips = poi.get("special_instructions", "")
        images = poi.get("images", {})
        image_urls = images.get("urls", []) if isinstance(images, dict) else []
        print(f"  {Color.GREEN}-{Color.RESET} {Color.BOLD}{name}{Color.RESET}")
        if desc:
            print(f"    {desc}")
        if addr:
            print(f"    {Color.DIM}Address:{Color.RESET} {addr}")
        if cost:
            print(f"    {Color.DIM}Cost:{Color.RESET} {cost}")
        if hours:
            print(f"    {Color.DIM}Hours:{Color.RESET} {hours}")
        if tips:
            print(f"    {Color.DIM}Tips:{Color.RESET} {tips}")
        print(f"    {Color.DIM}Images:{Color.RESET} {len(image_urls)}")


def display_requirements(data: list):
    count = len(data)
    print(f"\n{Color.YELLOW}{Color.BOLD}[Requirements]{Color.RESET} ({count} total)")
    for req in data:
        desc = req.get("description", "?")
        priority = req.get("priority", "")
        print(f"  {Color.YELLOW}-{Color.RESET} {desc} [{priority}]")


def display_plan(data: list):
    count = len(data)
    print(f"\n{Color.MAGENTA}{Color.BOLD}[Plan]{Color.RESET} ({count} option(s))")
    for i, option in enumerate(data, 1):
        days = option.get("days", [])
        cost = option.get("overall_cost", "")
        notes = option.get("general_notes", "")
        print(f"\n  {Color.MAGENTA}{Color.BOLD}Option {i}{Color.RESET}: {len(days)} day(s), {cost}")
        if notes:
            print(f"  {Color.DIM}{notes}{Color.RESET}")
        for d, day in enumerate(days, 1):
            highlight = day.get("highlight", "")
            lodging = day.get("lodging", "")
            blocks = day.get("blocks", [])
            print(f"\n    {Color.BOLD}Day {d}: {highlight}{Color.RESET}")
            if lodging:
                print(f"    {Color.DIM}Lodging:{Color.RESET} {lodging}")
            for block in blocks:
                time = block.get("time", "")
                desc = block.get("description", "")
                transport = block.get("transportation")
                pois_in_block = block.get("pois", [])
                print(f"      {Color.CYAN}{time}{Color.RESET} — {desc}")
                if transport:
                    method = transport.get("method", "")
                    duration = transport.get("duration", "")
                    print(f"        {Color.DIM}Transport: {method} ({duration}){Color.RESET}")
                for p in pois_in_block:
                    print(f"        {Color.GREEN}> {p.get('name', '?')}{Color.RESET}")


def display_poi_images(data: dict):
    name = data.get("name", "?")
    images = data.get("images", {})
    urls = images.get("urls", []) if isinstance(images, dict) else []
    print(f"\n{Color.GREEN}[POI Images]{Color.RESET} {Color.BOLD}{name}{Color.RESET}: {len(urls)} image(s)")


def display_done():
    print(f"\n{Color.GREEN}{Color.BOLD}[Done]{Color.RESET} Processing complete.\n")


def display_error(message: str):
    print(f"\n{Color.RED}{Color.BOLD}[Error]{Color.RESET} {message}\n")


# ---------------------------------------------------------------------------
# Send a message over WebSocket and stream updates
# ---------------------------------------------------------------------------
def send_message(ws_url: str, message: str, state: ConversationState):
    payload = {
        "message": message,
        "pois": state.pois,
        "requirements": state.requirements,
        "plan": state.plan,
    }

    try:
        ws = websocket.create_connection(ws_url, timeout=120)
    except Exception as exc:
        display_error(f"Could not connect to {ws_url}: {exc}")
        return

    try:
        ws.send(json.dumps(payload))

        while True:
            raw = ws.recv()
            if not raw:
                break

            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "intents":
                display_intents(data.get("data", []))

            elif msg_type == "pois":
                pois = data.get("data", [])
                state.pois = pois
                display_pois(pois)

            elif msg_type == "requirements":
                reqs = data.get("data", [])
                state.requirements = reqs
                display_requirements(reqs)

            elif msg_type == "plan":
                plan_data = data.get("data", [])
                state.plan = plan_data
                display_plan(plan_data)

            elif msg_type == "poi_images":
                img_data = data.get("data", {})
                display_poi_images(img_data)
                # Merge images into existing POI state
                poi_name = img_data.get("name", "")
                images = img_data.get("images", {})
                urls = images.get("urls", []) if isinstance(images, dict) else []
                for poi in state.pois:
                    if poi.get("name") == poi_name:
                        poi["images"] = {"urls": urls}
                        break

            elif msg_type == "done":
                display_done()
                break

            elif msg_type == "error":
                display_error(data.get("message", "Unknown error"))
                break

            else:
                print(f"  {Color.DIM}[Unknown: {msg_type}] {raw[:200]}{Color.RESET}")

    except websocket.WebSocketTimeoutException:
        display_error("WebSocket timed out waiting for response (120s)")
    except websocket.WebSocketConnectionClosedException:
        display_error("Server closed the connection unexpectedly")
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Interrupted — returning to prompt.{Color.RESET}\n")
    except Exception as exc:
        display_error(f"Unexpected error: {exc}")
    finally:
        try:
            ws.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------
HELP_TEXT = f"""\
{Color.BOLD}Slash commands:{Color.RESET}
  /health  — Run a health check against the server
  /state   — Show accumulated conversation state (POIs, requirements, plan)
  /reset   — Clear conversation state
  /help    — Show this help message
  /quit    — Exit the CLI
"""


def handle_slash(cmd: str, base_url: str, state: ConversationState) -> bool:
    """Handle a slash command. Returns True if the REPL should continue."""
    cmd = cmd.strip().lower()

    if cmd in ("/quit", "/exit", "/q"):
        return False
    elif cmd == "/health":
        health_check(base_url)
    elif cmd == "/state":
        print(state.summary())
    elif cmd == "/reset":
        state.reset()
        print(f"{Color.GREEN}State cleared.{Color.RESET}")
    elif cmd == "/help":
        print(HELP_TEXT)
    else:
        print(f"{Color.YELLOW}Unknown command:{Color.RESET} {cmd}. Type /help for commands.")

    return True


# ---------------------------------------------------------------------------
# Main REPL
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="TravelPlanner CLI test tool")
    parser.add_argument("--host", default="127.0.0.1", help="Backend host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Backend port (default: 5000)")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    ws_url = f"ws://{args.host}:{args.port}/ws/chat"

    print(f"{Color.BOLD}TravelPlanner CLI{Color.RESET}")
    print(f"Server: {base_url}  |  WebSocket: {ws_url}")
    print(f"Type a message to send, or /help for commands.\n")

    health_check(base_url)
    print()

    state = ConversationState()

    while True:
        try:
            user_input = input(f"{Color.BLUE}> {Color.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Color.DIM}Goodbye.{Color.RESET}")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            if not handle_slash(user_input, base_url, state):
                print(f"{Color.DIM}Goodbye.{Color.RESET}")
                break
            continue

        send_message(ws_url, user_input, state)


if __name__ == "__main__":
    main()
