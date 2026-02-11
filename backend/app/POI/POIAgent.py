import json
import os
from typing import Any, Dict, Optional

from openai import OpenAI

from POI.ImageFetcher import flickr_photo_search
from POI.POIModel import POIModel

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
_openai_client = OpenAI()  # reads OPENAI_API_KEY from env

POI_SYSTEM_PROMPT = """\
You are a travel Points of Interest (POI) discovery assistant.

Given a location or topic, return a JSON array of points of interest. Each POI object must have:
- "name": string — the name of the place
- "description": string — a brief description of the place
- "geo_coordinate": {"lat": number, "lng": number} — latitude and longitude
- "poi_type": string — one of "restaurant", "lodge", "tourist_destination", or "unknown"
- "opening_hours": string — typical opening hours (optional but preferred)
- "address": string — full address (optional but preferred)
- "special_instructions": string — tips for visitors (optional but preferred)
- "cost": string — entry cost or price range as a string (e.g. "Free", "$15", "¥2,000")

Do NOT include an "images" field — images are fetched separately.

Return ONLY a JSON array of POI objects. Do not wrap it in another object.
If the user specifies a number of results, return exactly that many.
Default to 10-15 POIs if no count is specified.
Focus on popular, well-known, and highly-rated places.
"""


def _call_poi_agent(poi: str, number_of_poi: Optional[int] = None) -> str:
    user_message = poi
    if number_of_poi is not None:
        user_message = f"{poi}, return {number_of_poi} results"
    response = _openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": POI_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    output_text = response.choices[0].message.content or ""
    print(f"[POIAgent] response received: {output_text}")
    return output_text


def _send_to_poi_agent(
    poi: str,
    number_of_poi: Optional[int] = None,
    images_per_poi: Optional[int] = None,
) -> POIModel:
    last_error = None
    for attempt in range(1, 2):
        output_text = _call_poi_agent(poi, number_of_poi=number_of_poi)
        try:
            items = json.loads(output_text)
        except json.JSONDecodeError as exc:
            last_error = f"agent_response_not_json: {exc}"
            continue

        errors = POIModel.validate_json(items, require_images=False)
        if errors:
            last_error = "; ".join(errors)
            continue

        poi_model = POIModel.from_json(items, require_images=False)
        for item in poi_model.items:
            try:
                images = flickr_photo_search(
                    item.poi.name, per_page=images_per_poi or 10
                )
                print(f"[POIAgent] flickr images for '{item.poi.name}': {images}")
            except Exception as exc:
                item.poi.images = []
                continue
            urls = images.get("urls") if isinstance(images, dict) else None
            item.poi.images = urls if isinstance(urls, list) else []

        print("[POIAgent] POI data retrieving successful")
        return poi_model

    print(f"[POIAgent] validation failed after retries: {last_error}")
    return {"error": "poi_validation_failed", "details": last_error}


def add_poi(
    existing_poi: Any,
    poi_name: str,
    number_of_poi: Optional[int] = None,
    images_per_poi: Optional[int] = None,
) -> POIModel:
    try:
        existing_model = POIModel.from_json(
            existing_poi, require_images=True, allow_empty=True
        )
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    new_model = _send_to_poi_agent(
        poi_name, number_of_poi=number_of_poi, images_per_poi=images_per_poi
    )
    if isinstance(new_model, dict):
        raise ValueError(f"poi_agent_failed: {new_model}")

    combined = existing_model.items + new_model.items
    return POIModel(combined)


def remove_poi(existing_poi: Any, poi_name: str) -> POIModel:
    try:
        existing_model = POIModel.from_json(existing_poi, require_images=True, allow_empty=True)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    if not isinstance(poi_name, str) or not poi_name:
        raise ValueError(
            "invalid_poi_name: poi_name must be a non-empty string")

    filtered = [item for item in existing_model.items if item.poi.name != poi_name]
    return POIModel(filtered)
