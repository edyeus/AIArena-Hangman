import json
from typing import Optional

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from POI.POIModel import POIModel
from Planner.RequirementModel import RequirementModel
from Planner.PlanOptionModel import PlanOptionModel

ENDPOINT = "https://edyzhang2026-travel-resource.services.ai.azure.com/api/projects/edyzhang2026-travel"
AGENT_NAME = "Scheduler"

_project_client = AIProjectClient(
    endpoint=ENDPOINT, credential=DefaultAzureCredential()
)
_openai_client = _project_client.get_openai_client()
_agent = None


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
    agent = _get_agent()
    response = _openai_client.responses.create(
        input=[{"role": "user", "content": message}],
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    return getattr(response, "output_text", "")


def _get_agent():
    global _agent
    if _agent is None:
        _agent = _project_client.agents.get(agent_name=AGENT_NAME)
        print(f"[Planner] Retrieved agent: {_agent.name}")
    return _agent
