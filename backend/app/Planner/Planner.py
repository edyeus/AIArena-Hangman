import json
import os
from typing import Optional

from openai import OpenAI

from POI.POIModel import POIModel
from Planner.RequirementModel import RequirementModel
from Planner.PlanOptionModel import PlanOptionModel

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
_openai_client = OpenAI()  # reads OPENAI_API_KEY from env

PLANNER_SYSTEM_PROMPT = """\
You are a travel itinerary planner. Given a list of POIs and requirements, generate detailed day-by-day itinerary options.

Return a JSON object with an "options" array. Each option has:
- "overall_cost": string — estimated total cost (e.g. "$4,200")
- "general_notes": string — overview of this itinerary option
- "days": array of day objects, each with:
  - "highlight": string — the theme or highlight of this day
  - "lodging": string — recommended accommodation (optional)
  - "blocks": array of time block objects, each with:
    - "time": string — time range (e.g. "9:00 AM - 11:30 AM")
    - "description": string — what to do during this block
    - "pois": array of POI objects (optional), each with:
      - "name": string
      - "description": string
      - "geo_coordinate": {"lat": number, "lng": number}
    - "transportation": object (optional) with:
      - "duration": string (e.g. "20 minutes")
      - "method": string (e.g. "subway", "walking", "taxi")
      - "cost": number (optional, in local currency)

Rules:
- Generate 2-3 itinerary options with different styles (e.g. budget, balanced, premium).
- Respect all requirements (budget, duration, preferences).
- Schedule POIs logically by proximity and opening hours.
- Include meals, rest, and travel time between locations.
- Use the provided POIs; do not invent new ones unless needed for meals or lodging.
- Return ONLY valid JSON matching the schema above.
"""


def plan(
    poi_model: POIModel,
    requirement_model: RequirementModel,
    existing_plan: Optional[PlanOptionModel] = None,
) -> PlanOptionModel:
    payload = {
        "poi": poi_model.to_list(),
        "requirements": requirement_model.to_list(),
    }
    if existing_plan is not None:
        payload["options"] = existing_plan.to_list()

    message = json.dumps(payload, ensure_ascii=True)
    print(f"[Planner] sending to agent: {message}")
    output_text = _call_planner_agent(message)
    print(f"[Planner] raw response: {output_text}")

    try:
        response_data = json.loads(output_text)
        return PlanOptionModel.from_json(response_data)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"[Planner] failed to parse response: {exc}")
        return PlanOptionModel(items=[])


def _call_planner_agent(message: str) -> str:
    response = _openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    return response.choices[0].message.content or ""
