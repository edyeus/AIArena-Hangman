from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from POI.POIModel import SinglePOIWithCost, POIModel

# Example valid input for from_json:
# {
#     "options": [
#         {
#             "overall_cost": "$4200",
#             "general_notes": "A 2-day cultural tour of Tokyo focusing on temples and local cuisine.",
#             "days": [
#                 {
#                     "highlight": "Explore Asakusa and traditional temples",
#                     "lodging": "Ryokan in Asakusa",
#                     "blocks": [
#                         {
#                             "time": "9:00 AM - 11:30 AM",
#                             "description": "Visit Senso-ji temple and walk through Nakamise shopping street",
#                             "pois": [
#                                 {
#                                     "name": "Senso-ji Temple",
#                                     "description": "Ancient Buddhist temple in Asakusa",
#                                     "geo_coordinate": {"lat": 35.7148, "lng": 139.7929}
#                                 }
#                             ]
#                         },
#                         {
#                             "time": "12:00 PM - 1:00 PM",
#                             "description": "Lunch at a local soba restaurant",
#                             "transportation": {
#                                 "duration": "10 minutes",
#                                 "method": "walking"
#                             }
#                         },
#                         {
#                             "time": "2:00 PM - 4:30 PM",
#                             "description": "Tour Ueno Park and the National Museum",
#                             "transportation": {
#                                 "duration": "20 minutes",
#                                 "method": "subway",
#                                 "cost": 3.5
#                             },
#                             "pois": [
#                                 {
#                                     "name": "Ueno Park",
#                                     "description": "Historic park known for cherry blossoms",
#                                     "geo_coordinate": {"lat": 35.7146, "lng": 139.7744}
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "highlight": "Modern Tokyo — Shibuya and Shinjuku",
#                     "lodging": "Hotel in Shinjuku",
#                     "blocks": [
#                         {
#                             "time": "10:00 AM - 12:00 PM",
#                             "description": "Explore Shibuya Crossing and surrounding shops",
#                             "pois": [
#                                 {
#                                     "name": "Shibuya Crossing",
#                                     "description": "Famous multi-way pedestrian intersection",
#                                     "geo_coordinate": {"lat": 35.6762, "lng": 139.6503}
#                                 }
#                             ]
#                         },
#                         {
#                             "time": "3:00 PM - 5:00 PM",
#                             "description": "Relax at Meiji Shrine gardens",
#                             "transportation": {
#                                 "duration": "15 minutes",
#                                 "method": "taxi",
#                                 "cost": 12.0
#                             }
#                         }
#                     ]
#                 }
#             ]
#         }
#     ]
# }


@dataclass
class Transportation:
    duration: str
    method: str
    cost: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "duration": self.duration,
            "method": self.method,
        }
        if self.cost is not None:
            data["cost"] = self.cost
        return data


@dataclass
class Block:
    time: str
    description: str
    pois: Optional[List[SinglePOIWithCost]] = None
    transportation: Optional[Transportation] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "time": self.time,
            "description": self.description,
        }
        if self.pois is not None:
            data["pois"] = [poi.to_dict() for poi in self.pois]
        if self.transportation is not None:
            data["transportation"] = self.transportation.to_dict()
        return data


@dataclass
class Day:
    highlight: str
    blocks: List[Block]
    lodging: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "highlight": self.highlight,
            "blocks": [block.to_dict() for block in self.blocks],
        }
        if self.lodging is not None:
            data["lodging"] = self.lodging
        return data


@dataclass
class SinglePlanOption:
    days: List[Day]
    overall_cost: str
    general_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "days": [day.to_dict() for day in self.days],
            "overall_cost": self.overall_cost,
            "general_notes": self.general_notes,
        }


class PlanOptionModel:
    def __init__(self, items: List[SinglePlanOption]) -> None:
        self.items = items

    def to_list(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.items]

    @staticmethod
    def _normalize_input(data: Any) -> Optional[List[Dict[str, Any]]]:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            items = data.get("options")
            if isinstance(items, list):
                return items
        return None

    @classmethod
    def from_json(cls, data: Any, allow_empty: bool = False) -> "PlanOptionModel":
        options_data = cls._normalize_input(data)
        if options_data is None:
            raise ValueError("invalid_plan_option_input")
        if not options_data and not allow_empty:
            raise ValueError("options list is empty")

        items: List[SinglePlanOption] = []
        for idx, option in enumerate(options_data):
            items.append(_parse_option(option, idx))
        return cls(items)

    @classmethod
    def validate_json(cls, data: Any, allow_empty: bool = False) -> List[str]:
        errors: List[str] = []
        options = cls._normalize_input(data)
        if options is None:
            return ["options must be a list or object with options list"]
        if not options and not allow_empty:
            return ["options list is empty"]

        for idx, option in enumerate(options):
            errors.extend(_validate_option(option, idx))
        return errors


# ---------------------------------------------------------------------------
# Parsing helpers (from_json path – raise on first error)
# ---------------------------------------------------------------------------


def _parse_option(option: Any, idx: int) -> SinglePlanOption:
    if not isinstance(option, dict):
        raise ValueError(f"options[{idx}] must be an object")

    overall_cost = option.get("overall_cost")
    if not isinstance(overall_cost, str) or not overall_cost:
        raise ValueError(f"options[{idx}].overall_cost is required")

    general_notes = option.get("general_notes")
    if not isinstance(general_notes, str) or not general_notes:
        raise ValueError(f"options[{idx}].general_notes is required")

    days_data = option.get("days")
    if not isinstance(days_data, list) or not days_data:
        raise ValueError(f"options[{idx}].days must be a non-empty list")

    days: List[Day] = []
    for d_idx, day_data in enumerate(days_data):
        days.append(_parse_day(day_data, idx, d_idx))

    return SinglePlanOption(days=days, overall_cost=overall_cost, general_notes=general_notes)


def _parse_day(day_data: Any, opt_idx: int, day_idx: int) -> Day:
    prefix = f"options[{opt_idx}].days[{day_idx}]"
    if not isinstance(day_data, dict):
        raise ValueError(f"{prefix} must be an object")

    highlight = day_data.get("highlight")
    if not isinstance(highlight, str) or not highlight:
        raise ValueError(f"{prefix}.highlight is required")

    blocks_data = day_data.get("blocks")
    if not isinstance(blocks_data, list) or not blocks_data:
        raise ValueError(f"{prefix}.blocks must be a non-empty list")

    blocks: List[Block] = []
    for b_idx, block_data in enumerate(blocks_data):
        blocks.append(_parse_block(block_data, opt_idx, day_idx, b_idx))

    lodging = day_data.get("lodging")
    if lodging is not None and not isinstance(lodging, str):
        lodging = None

    return Day(highlight=highlight, blocks=blocks, lodging=lodging)


def _parse_block(block_data: Any, opt_idx: int, day_idx: int, block_idx: int) -> Block:
    prefix = f"options[{opt_idx}].days[{day_idx}].blocks[{block_idx}]"
    if not isinstance(block_data, dict):
        raise ValueError(f"{prefix} must be an object")

    time = block_data.get("time")
    if not isinstance(time, str) or not time:
        raise ValueError(f"{prefix}.time is required")

    description = block_data.get("description")
    if not isinstance(description, str) or not description:
        raise ValueError(f"{prefix}.description is required")

    pois: Optional[List[SinglePOIWithCost]] = None
    pois_data = block_data.get("pois")
    if pois_data is not None:
        if not isinstance(pois_data, list):
            raise ValueError(f"{prefix}.pois must be a list")
        poi_model = POIModel.from_json(pois_data, require_images=False)
        pois = poi_model.items

    transportation: Optional[Transportation] = None
    transport_data = block_data.get("transportation")
    if transport_data is not None:
        transportation = _parse_transportation(transport_data, prefix)

    return Block(time=time, description=description, pois=pois, transportation=transportation)


def _parse_transportation(data: Any, prefix: str) -> Transportation:
    if not isinstance(data, dict):
        raise ValueError(f"{prefix}.transportation must be an object")

    duration = data.get("duration")
    if not isinstance(duration, str) or not duration:
        raise ValueError(f"{prefix}.transportation.duration is required")

    method = data.get("method")
    if not isinstance(method, str) or not method:
        raise ValueError(f"{prefix}.transportation.method is required")

    cost: Optional[float] = None
    cost_raw = data.get("cost")
    if cost_raw is not None:
        if not isinstance(cost_raw, (int, float)):
            raise ValueError(f"{prefix}.transportation.cost must be a number")
        cost = cost_raw

    return Transportation(duration=duration, method=method, cost=cost)


# ---------------------------------------------------------------------------
# Validation helpers (validate_json path – collect all errors)
# ---------------------------------------------------------------------------


def _validate_option(option: Any, idx: int) -> List[str]:
    errors: List[str] = []
    if not isinstance(option, dict):
        return [f"options[{idx}] must be an object"]

    overall_cost = option.get("overall_cost")
    if not isinstance(overall_cost, str) or not overall_cost:
        errors.append(f"options[{idx}].overall_cost is required")

    general_notes = option.get("general_notes")
    if not isinstance(general_notes, str) or not general_notes:
        errors.append(f"options[{idx}].general_notes is required")

    days_data = option.get("days")
    if not isinstance(days_data, list) or not days_data:
        errors.append(f"options[{idx}].days must be a non-empty list")
    else:
        for d_idx, day_data in enumerate(days_data):
            errors.extend(_validate_day(day_data, idx, d_idx))

    return errors


def _validate_day(day_data: Any, opt_idx: int, day_idx: int) -> List[str]:
    errors: List[str] = []
    prefix = f"options[{opt_idx}].days[{day_idx}]"
    if not isinstance(day_data, dict):
        return [f"{prefix} must be an object"]

    highlight = day_data.get("highlight")
    if not isinstance(highlight, str) or not highlight:
        errors.append(f"{prefix}.highlight is required")

    blocks_data = day_data.get("blocks")
    if not isinstance(blocks_data, list) or not blocks_data:
        errors.append(f"{prefix}.blocks must be a non-empty list")
    else:
        for b_idx, block_data in enumerate(blocks_data):
            errors.extend(_validate_block(block_data, opt_idx, day_idx, b_idx))

    return errors


def _validate_block(block_data: Any, opt_idx: int, day_idx: int, block_idx: int) -> List[str]:
    errors: List[str] = []
    prefix = f"options[{opt_idx}].days[{day_idx}].blocks[{block_idx}]"
    if not isinstance(block_data, dict):
        return [f"{prefix} must be an object"]

    time = block_data.get("time")
    if not isinstance(time, str) or not time:
        errors.append(f"{prefix}.time is required")

    description = block_data.get("description")
    if not isinstance(description, str) or not description:
        errors.append(f"{prefix}.description is required")

    pois_data = block_data.get("pois")
    if pois_data is not None:
        if not isinstance(pois_data, list):
            errors.append(f"{prefix}.pois must be a list")
        else:
            poi_errors = POIModel.validate_json(
                pois_data, require_images=False)
            for err in poi_errors:
                errors.append(f"{prefix}.pois: {err}")

    transport_data = block_data.get("transportation")
    if transport_data is not None:
        errors.extend(_validate_transportation(transport_data, prefix))

    return errors


def _validate_transportation(data: Any, prefix: str) -> List[str]:
    errors: List[str] = []
    if not isinstance(data, dict):
        return [f"{prefix}.transportation must be an object"]

    duration = data.get("duration")
    if not isinstance(duration, str) or not duration:
        errors.append(f"{prefix}.transportation.duration is required")

    method = data.get("method")
    if not isinstance(method, str) or not method:
        errors.append(f"{prefix}.transportation.method is required")

    cost = data.get("cost")
    if cost is not None and not isinstance(cost, (int, float)):
        errors.append(f"{prefix}.transportation.cost must be a number")

    return errors
