import json
import os
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
FLICKR_REST_URL = "https://api.flickr.com/services/rest/"


def google_text_search_place(
    location_name: str,
    api_key: Optional[str] = None,
    field_mask: Optional[str] = None,
) -> dict:
    if not location_name:
        raise ValueError("location_name is required")
    key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("Google Maps API key is required")
    mask = field_mask or "places.displayName,places.formattedAddress,places.id"

    body = json.dumps({"textQuery": location_name}).encode("utf-8")
    req = Request(
        TEXT_SEARCH_URL,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": mask,
        },
        method="POST",
    )

    with urlopen(req, timeout=15) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def flickr_photo_search_internal(
    location_name: str,
    api_key: Optional[str] = None,
    per_page: int = 10,
    page: int = 1,
    extras: Optional[str] = None,
) -> dict:
    if not location_name:
        raise ValueError("location_name is required")
    key = api_key or os.getenv("FLICKR_API_KEY")
    if not key:
        raise ValueError("Flickr API key is required")

    params = {
        "method": "flickr.photos.search",
        "api_key": key,
        "text": location_name,
        "per_page": per_page,
        "page": page,
        "format": "json",
        "nojsoncallback": 1,
    }
    if extras:
        params["extras"] = extras

    url = f"{FLICKR_REST_URL}?{urlencode(params)}"
    req = Request(url, headers={"Accept": "application/json"})

    with urlopen(req, timeout=15) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def flickr_photo_search(
    location_name: str,
    api_key: Optional[str] = None,
    per_page: int = 10,
    page: int = 1,
    extras: Optional[str] = None,
) -> dict:
    # Expected output:
    # {"urls":["https://live.staticflickr.com/65535/54957725380_f703109d69_c.jpg","https://live.staticflickr.com/65535/54863632112_b5b8d1f8a5_c.jpg","https://live.staticflickr.com/65535/54551507602_b09c89abb3_c.jpg","https://live.staticflickr.com/65535/54551507357_2840bce8b4_c.jpg","https://live.staticflickr.com/65535/54429358144_5f50f7169a_c.jpg","https://live.staticflickr.com/65535/54393752838_33d359d099_c.jpg","https://live.staticflickr.com/65535/54392643712_4e4f0c0808_c.jpg","https://live.staticflickr.com/65535/54392643607_c7ee1ea4e6_c.jpg","https://live.staticflickr.com/65535/54393752478_5e638b5456_c.jpg","https://live.staticflickr.com/65535/54393752218_ffca740775_c.jpg"]}
    result = flickr_photo_search_internal(
        location_name=location_name,
        api_key=api_key,
        per_page=per_page,
        page=page,
        extras=extras,
    )
    photos = result.get("photos", {}).get("photo", [])
    urls = []
    for photo in photos:
        server = photo.get("server")
        photo_id = photo.get("id")
        secret = photo.get("secret")
        if server and photo_id and secret:
            urls.append(
                f"https://live.staticflickr.com/{server}/{photo_id}_{secret}_c.jpg")
    return {"urls": urls}
