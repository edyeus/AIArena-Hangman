from flask import Flask, request
from flask_cors import CORS

from POI.ImageFetcher import flickr_photo_search
from POI.POIAgent import add_poi
from Orchestrator import analyze_intents
from Planner import plan
from Planner.RequirementModel import RequirementModel

app = Flask(__name__)
CORS(app)


@app.get("/health")
def health_check() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.post("/chat")
def chat() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "")
    if not message:
        return {"error": "message is required"}, 400
    try:
        intents_payload = analyze_intents(message)
    except Exception as exc:
        return {"error": "intent_request_failed", "details": str(exc)}, 502
    return intents_payload, 200

# curl -X POST http://127.0.0.1:5000/testpoi -H "Content-Type: application/json" -d '{"poi_name":"Seattle", "poi":{"poi":[]}}'


@app.post("/testpoi")
def testpoi() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    existing_poi = payload.get("poi")
    poi_name = payload.get("poi_name", "")
    if not isinstance(existing_poi, dict):
        return {"error": "poi is required"}, 400
    if not poi_name:
        return {"error": "poi_name is required"}, 400
    try:
        result = add_poi(existing_poi, poi_name,
                         number_of_poi=3, images_per_poi=3).to_list()
    except Exception as exc:
        return {"error": "poi_add_failed", "details": str(exc)}, 502
    return {"poi": result}, 200


# curl -X POST http://127.0.0.1:5000/testingplanner -H "Content-Type: application/json" -d '{
#   "poi_name": "Tokyo",
#   "poi": {"poi": []},
#   "requirements": [
#     {"description": "Budget under $5000 total", "priority": "must_have"},
#     {"description": "Prefer staying in traditional ryokan"},
#     {"description": "Avoid crowded tourist spots", "priority": "avoid"}
#   ]
# }'


@app.post("/testingplanner")
def testingplanner() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    existing_poi = payload.get("poi")
    poi_name = payload.get("poi_name", "")
    requirements = payload.get("requirements")

    if not isinstance(existing_poi, dict):
        return {"error": "poi is required"}, 400
    if not poi_name:
        return {"error": "poi_name is required"}, 400
    if requirements is None:
        return {"error": "requirements is required"}, 400

    try:
        poi_model = add_poi(existing_poi, poi_name,
                            number_of_poi=3, images_per_poi=3)
        requirement_model = RequirementModel.from_json(requirements)
        plan_result = plan(poi_model, requirement_model)
    except Exception as exc:
        return {"error": "planner_failed", "details": str(exc)}, 502
    return {"options": plan_result.to_list()}, 200
