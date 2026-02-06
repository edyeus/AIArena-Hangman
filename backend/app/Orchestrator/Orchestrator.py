import json
from typing import Any, Dict, List, Optional

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from POI.POIAgent import add_poi
from POI.POIModel import POIModel
from Planner import plan
from Planner.RequirementModel import RequirementModel

ENDPOINT = "https://edyzhang2026-travel-resource.services.ai.azure.com/api/projects/edyzhang2026-travel"
AGENT_NAME = "Orchestrator"
MAX_ATTEMPTS = 2

_project_client = AIProjectClient(
    endpoint=ENDPOINT, credential=DefaultAzureCredential()
)
_openai_client = _project_client.get_openai_client()
_agent = None

INTENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intents": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": [
                            "Points_Of_Interest",
                            "Schedule_Requirement",
                            "Schedule_Option",
                            "Not_Relevant",
                            "General_Response",
                        ],
                    },
                    "action": {
                        "type": "string",
                        "enum": ["add", "remove", "modify"],
                    },
                    "value": {"type": "string"},
                    "response": {"type": "string"},
                },
                "required": ["intent", "value"],
            },
        }
    },
    "required": ["intents"],
}


def analyze_intents(message: str) -> Dict[str, Any]:
    print(f"[Orchestrator] analyze_intents: {message}")
    last_error: Optional[str] = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        output_text = _call_orchestrator_agent(message)
        print(f"[Orchestrator] intent raw response: {output_text}")

        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError as exc:
            last_error = f"invalid_json: {exc}"
            continue

        errors = _validate_intents(payload)
        if not errors:
            print("[Orchestrator] intent validation successful")
            return _build_and_plan(payload)

        last_error = "; ".join(errors)

    print(f"[Orchestrator] intent validation failed: {last_error}")
    return {
        "intents": [
            {"intent": "General_Response", "value": "We're working on it."}
        ]
    }


def _call_orchestrator_agent(message: str) -> str:
    agent = _get_agent()
    response = _openai_client.responses.create(
        input=[{"role": "user", "content": message}],
        extra_body={"agent": {"name": agent.name,
                              "type": "agent_reference"}},
    )
    return getattr(response, "output_text", "")


def _get_agent():
    global _agent
    if _agent is None:
        _agent = _project_client.agents.get(agent_name=AGENT_NAME)
        print(f"[Orchestrator] Retrieved agent: {_agent.name}")
    return _agent


def _validate_intents(payload: Any) -> List[str]:
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload must be an object"]
    intents = payload.get("intents")
    if not isinstance(intents, list) or not intents:
        return ["intents must be a non-empty list"]

    for idx, intent in enumerate(intents):
        if not isinstance(intent, dict):
            errors.append(f"intent[{idx}] must be an object")
            continue
        intent_type = intent.get("intent")
        action = intent.get("action")
        value = intent.get("value")
        response = intent.get("response")

        if intent_type not in {
            "Points_Of_Interest",
            "Schedule_Requirement",
            "Schedule_Option",
            "Not_Relevant",
            "General_Response",
        }:
            errors.append(f"intent[{idx}].intent is invalid")
            continue

        if not isinstance(value, str) or not value:
            errors.append(f"intent[{idx}].value must be a non-empty string")

        if intent_type == "Points_Of_Interest":
            if action not in {"add", "remove"}:
                errors.append(f"intent[{idx}].action must be add/remove")
        elif intent_type == "Schedule_Requirement":
            if action not in {"add", "remove"}:
                errors.append(f"intent[{idx}].action must be add/remove")
        elif intent_type == "Schedule_Option":
            if action not in {"add", "modify", "remove"}:
                errors.append(
                    f"intent[{idx}].action must be add/modify/remove")
        elif intent_type == "Not_Relevant":
            if not isinstance(response, str) or not response:
                errors.append(
                    f"intent[{idx}].response is required for Not_Relevant"
                )
        elif intent_type == "General_Response":
            if not isinstance(value, str) or not value:
                errors.append(
                    f"intent[{idx}].value is required for General_Response"
                )

    return errors


def _build_and_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    intents = payload.get("intents", [])
    poi_intents = [
        intent
        for intent in intents
        if intent.get("intent") == "Points_Of_Interest"
        and intent.get("action") == "add"
    ]
    requirement_intents = [
        intent
        for intent in intents
        if intent.get("intent") == "Schedule_Requirement"
        and intent.get("action") == "add"
    ]

    poi_model = POIModel(items=[])
    for intent in poi_intents:
        poi_name = intent.get("value", "")
        if not poi_name:
            continue
        poi_model = add_poi(poi_model.to_list(), poi_name)

    requirement_model = RequirementModel.from_json(
        [{"description": intent.get("value", "")} for intent in requirement_intents if intent.get("value")],
        allow_empty=True,
    )

    print(f"[Orchestrator] poi: {json.dumps(poi_model.to_list(), ensure_ascii=True)}")
    print(f"[Orchestrator] requirements: {json.dumps(requirement_model.to_list(), ensure_ascii=True)}")
    planner_result = plan(poi_model, requirement_model)
    combined = {
        "intents": intents,
        "pois": poi_model.to_list(),
        "planner": planner_result.to_list(),
    }
    return combined
