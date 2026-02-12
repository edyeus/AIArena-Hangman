from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class POIType(Enum):
    RESTAURANT = "restaurant"
    LODGE = "lodge"
    TOURIST_DESTINATION = "tourist_destination"
    UNKNOWN = "unknown"


@dataclass
class GeoCoordinate:
    lat: float
    lng: float

    def to_dict(self) -> Dict[str, Any]:
        return {"lat": self.lat, "lng": self.lng}


@dataclass
class SinglePOI:
    name: str
    description: str
    geo_coordinate: GeoCoordinate
    poi_type: POIType = POIType.UNKNOWN
    images: Optional[List[str]] = None
    opening_hours: Optional[str] = None
    address: Optional[str] = None
    special_instructions: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "geo_coordinate": self.geo_coordinate.to_dict(),
            "poi_type": self.poi_type.value,
        }
        if self.opening_hours:
            data["opening_hours"] = self.opening_hours
        if self.address:
            data["address"] = self.address
        if self.special_instructions:
            data["special_instructions"] = self.special_instructions
        if self.images is not None:
            data["images"] = {"urls": self.images}
        return data


@dataclass
class SinglePOIWithCost:
    poi: SinglePOI
    cost: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = self.poi.to_dict()
        data["cost"] = self.cost
        return data


class POIModel:
    def __init__(self, items: List[SinglePOIWithCost]) -> None:
        self.items = items

    def to_list(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.items]

    @staticmethod
    def _normalize_input(data: Any) -> Optional[List[Dict[str, Any]]]:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Check common wrapper keys the model might use
            for key in ("poi", "pois", "results", "points_of_interest"):
                items = data.get(key)
                if isinstance(items, list):
                    return items
            # Fallback: use the first list value found in the dict
            for value in data.values():
                if isinstance(value, list):
                    return value
            # Single POI object (has "name" key) — wrap in a list
            if "name" in data:
                return [data]
        return None

    @classmethod
    def from_json(
        cls, data: Any, require_images: bool = True, allow_empty: bool = False
    ) -> "POIModel":
        items_data = cls._normalize_input(data)
        if items_data is None:
            raise ValueError("invalid_poi_input")
        if not items_data and not allow_empty:
            raise ValueError("poi list is empty")

        items: List[SinglePOIWithCost] = []
        for idx, item in enumerate(items_data):
            if not isinstance(item, dict):
                raise ValueError(f"items[{idx}] must be an object")

            name = item.get("name")
            if not isinstance(name, str) or not name:
                raise ValueError(f"items[{idx}].name is required")

            description = item.get("description")
            if not isinstance(description, str) or not description:
                raise ValueError(f"items[{idx}].description is required")

            geo = item.get("geo_coordinate")
            if not isinstance(geo, dict):
                raise ValueError(
                    f"items[{idx}].geo_coordinate must be an object")
            lat = geo.get("lat")
            lng = geo.get("lng")
            if not isinstance(lat, (int, float)):
                raise ValueError(
                    f"items[{idx}].geo_coordinate.lat must be a number"
                )
            if not isinstance(lng, (int, float)):
                raise ValueError(
                    f"items[{idx}].geo_coordinate.lng must be a number"
                )

            images: Optional[List[str]] = None
            if "images" in item and isinstance(item["images"], dict):
                urls = item["images"].get("urls")
                if isinstance(urls, list):
                    valid_urls = [
                        url for url in urls if isinstance(url, str) and _is_valid_url(url)
                    ]
                    images = valid_urls
            if require_images and images is None:
                raise ValueError(f"items[{idx}].images.urls is required")

            opening_hours = item.get("opening_hours")
            if opening_hours is not None and not isinstance(opening_hours, str):
                opening_hours = None

            address = item.get("address")
            if address is not None and not isinstance(address, str):
                address = None

            special_instructions = item.get("special_instructions")
            if special_instructions is not None and not isinstance(
                special_instructions, str
            ):
                special_instructions = None

            poi_type_raw = item.get("poi_type")
            if poi_type_raw is None:
                poi_type = POIType.TOURIST_DESTINATION
            else:
                try:
                    poi_type = POIType(poi_type_raw)
                except ValueError:
                    poi_type = POIType.TOURIST_DESTINATION

            cost_raw = item.get("cost")
            cost = cost_raw if isinstance(cost_raw, str) else ""

            items.append(
                SinglePOIWithCost(
                    poi=SinglePOI(
                        name=name,
                        description=description,
                        geo_coordinate=GeoCoordinate(lat=lat, lng=lng),
                        poi_type=poi_type,
                        images=images,
                        opening_hours=opening_hours,
                        address=address,
                        special_instructions=special_instructions,
                    ),
                    cost=cost,
                )
            )
        return cls(items)

    @classmethod
    def validate_json(
        cls, data: Any, require_images: bool = True, allow_empty: bool = False
    ) -> List[str]:
        errors: List[str] = []
        items = cls._normalize_input(data)
        if items is None:
            return ["poi must be a list or object with results/poi list"]
        if not items and not allow_empty:
            return ["poi list is empty"]

        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"items[{idx}] must be an object")
                continue
            name = item.get("name")
            description = item.get("description")
            geo = item.get("geo_coordinate")
            if not isinstance(name, str) or not name:
                errors.append(f"items[{idx}].name is required")
            if not isinstance(description, str) or not description:
                errors.append(f"items[{idx}].description is required")
            if not isinstance(geo, dict):
                errors.append(f"items[{idx}].geo_coordinate must be an object")
            else:
                lat = geo.get("lat")
                lng = geo.get("lng")
                if not isinstance(lat, (int, float)):
                    errors.append(
                        f"items[{idx}].geo_coordinate.lat must be a number")
                if not isinstance(lng, (int, float)):
                    errors.append(
                        f"items[{idx}].geo_coordinate.lng must be a number")
            if require_images:
                images = item.get("images")
                if not isinstance(images, dict):
                    errors.append(f"items[{idx}].images must be an object")
                else:
                    urls = images.get("urls")
                    if not isinstance(urls, list):
                        errors.append(
                            f"items[{idx}].images.urls must be an array")

        return errors


def _is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
