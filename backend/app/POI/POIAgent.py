# Before running the sample:
#    pip install --pre azure-ai-projects>=2.0.0b1
#    pip install azure-identity

import json
from typing import Any, Dict, Optional

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from POI.ImageFetcher import flickr_photo_search
from POI.POIModel import POIModel

ENDPOINT = "https://edyzhang2026-travel-resource.services.ai.azure.com/api/projects/edyzhang2026-travel"
AGENT_NAME = "POI"

_project_client = AIProjectClient(
    endpoint=ENDPOINT,
    credential=DefaultAzureCredential(),
)
_openai_client = _project_client.get_openai_client()
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        _agent = _project_client.agents.get(agent_name=AGENT_NAME)
    return _agent


def _call_poi_agent(poi: str, number_of_poi: Optional[int] = None) -> str:
    if number_of_poi is not None:
        poi = f"{poi}, return {number_of_poi} results"
    agent = _get_agent()
    response = _openai_client.responses.create(
        input=[{"role": "user", "content": poi}],
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    output_text = getattr(response, "output_text", "")
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
        existing_model = POIModel.from_json(existing_poi, require_images=True)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    if not isinstance(poi_name, str) or not poi_name:
        raise ValueError(
            "invalid_poi_name: poi_name must be a non-empty string")

    filtered = [item for item in existing_model.items if item.name != poi_name]
    return POIModel(filtered)
