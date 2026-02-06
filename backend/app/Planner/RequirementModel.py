from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class Priority(Enum):
    MUST_HAVE = "must_have"
    PREFERRED = "preferred"
    AVOID = "avoid"


@dataclass
class Requirement:
    description: str
    priority: Priority

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "priority": self.priority.value,
        }


# Example valid inputs for from_json:
#
# 1) Bare list, priority omitted (defaults to "preferred"):
# [
#     {"description": "No more than 2 hours of driving per day"},
#     {"description": "Must visit at least one national park", "priority": "must_have"},
#     {"description": "Avoid staying in hostels", "priority": "avoid"}
# ]
#
# 2) Wrapped in an object:
# {
#     "requirements": [
#         {"description": "Budget under $3000 total", "priority": "must_have"},
#         {"description": "Prefer beach destinations"}
#     ]
# }


class RequirementModel:
    def __init__(self, items: List[Requirement]) -> None:
        self.items = items

    def to_list(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.items]

    @staticmethod
    def _normalize_input(data: Any) -> Optional[List[Dict[str, Any]]]:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            items = data.get("requirements")
            if isinstance(items, list):
                return items
        return None

    @classmethod
    def from_json(cls, data: Any, allow_empty: bool = False) -> "RequirementModel":
        items_data = cls._normalize_input(data)
        if items_data is None:
            raise ValueError("invalid_requirement_input")
        if not items_data and not allow_empty:
            raise ValueError("requirements list is empty")

        items: List[Requirement] = []
        for idx, item in enumerate(items_data):
            if not isinstance(item, dict):
                raise ValueError(f"items[{idx}] must be an object")

            description = item.get("description")
            if not isinstance(description, str) or not description:
                raise ValueError(f"items[{idx}].description is required")

            priority_raw = item.get("priority")
            if priority_raw is None:
                priority = Priority.PREFERRED
            elif not isinstance(priority_raw, str):
                raise ValueError(
                    f'items[{idx}].priority must be one of: must_have, preferred, avoid'
                )
            else:
                try:
                    priority = Priority(priority_raw)
                except ValueError:
                    raise ValueError(
                        f'items[{idx}].priority must be one of: must_have, preferred, avoid'
                    )

            items.append(Requirement(description=description, priority=priority))

        return cls(items)

    @classmethod
    def validate_json(cls, data: Any, allow_empty: bool = False) -> List[str]:
        errors: List[str] = []
        items = cls._normalize_input(data)
        if items is None:
            return ["requirements must be a list or object with requirements list"]
        if not items and not allow_empty:
            return ["requirements list is empty"]

        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"items[{idx}] must be an object")
                continue
            description = item.get("description")
            if not isinstance(description, str) or not description:
                errors.append(f"items[{idx}].description is required")

        return errors