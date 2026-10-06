"""Load and validate fictional, local-only demonstration fixtures."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bhomi.config import DATA_DIR

FILES = {
    "farms": "demo_farms.json", "weather": "demo_weather.json",
    "prices": "demo_prices.json", "alerts": "demo_alerts.json",
    "advisories": "demo_advisories.json", "crop_cases": "demo_crop_cases.json",
}
ENGLISH_FIELDS = {
    "farms": ("name_en", "crop_en", "stage_en", "last_irrigation_en", "recent_activity_en", "source_label_en", "observed_at_en"),
    "weather": ("summary_en", "why_en", "source_label_en", "as_of_en"),
    "prices": ("crop_en", "market_en", "source_label_en", "as_of_en"),
    "alerts": ("title_en", "reason_en", "source_label_en", "as_of_en"),
    "advisories": ("crop_en", "stage_en", "advice_en", "reason_en", "source_label_en", "as_of_en"),
    "crop_cases": ("title_en", "result_en", "source_label_en"),
}


class DemoDataError(ValueError):
    """Raised when a demo fixture is missing or unsafe to display."""


def _records(value: Any, name: str) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        candidates = value.get("fields") if name == "farms" else [value.get("farmer", {})]
        return [x for x in candidates if isinstance(x, dict)]
    return value if isinstance(value, list) else []


def validate_data(data: dict[str, Any]) -> None:
    for name in FILES:
        if name not in data:
            raise DemoDataError(f"Missing fixture: {name}")
        records = _records(data[name], name)
        if not records:
            raise DemoDataError(f"Fixture has no records: {name}")
        for index, record in enumerate(records):
            label = f"{name}[{index}]"
            if record.get("is_demo") is not True:
                raise DemoDataError(f"{label} must be marked is_demo=true")
            if not record.get("source_label"):
                raise DemoDataError(f"{label} requires source_label")
            time_field = "as_of" if name in {"weather", "prices", "alerts", "advisories"} else "observed_at"
            if name in {"weather", "prices", "alerts", "advisories", "farms"} and not record.get(time_field):
                raise DemoDataError(f"{label} requires {time_field}")
            missing_english = [key for key in ENGLISH_FIELDS[name] if not record.get(key)]
            if missing_english:
                raise DemoDataError(f"{label} requires English fields: {', '.join(missing_english)}")
    farmer = data["farms"].get("farmer", {})
    if farmer.get("is_demo") is not True or not farmer.get("source_label"):
        raise DemoDataError("farms.farmer must include a demo label and source_label")
    if not all(farmer.get(key) for key in ("label_en", "location_en", "source_label_en")):
        raise DemoDataError("farms.farmer requires English display fields")
    farm_fields = data["farms"].get("fields", [])
    if not farm_fields or any(not field.get("polygon") for field in farm_fields):
        raise DemoDataError("Every sample field needs an illustrative polygon")
    field_ids = {field["id"] for field in farm_fields}
    if {row["field_id"] for row in data["weather"]} != field_ids:
        raise DemoDataError("Weather fixtures must match the sample field IDs")
    if {row["field_id"] for row in data["alerts"]} != field_ids:
        raise DemoDataError("Alert fixtures must match the sample field IDs")
    crops = {field["crop_gu"] for field in farm_fields}
    if not crops.issubset({row["crop_gu"] for row in data["prices"]}):
        raise DemoDataError("Every sample crop needs a mandi fixture")
    if not crops.issubset({row["crop_gu"] for row in data["advisories"]}):
        raise DemoDataError("Every sample crop needs an advisory fixture")


def load_demo_data(data_dir: Path = DATA_DIR) -> dict[str, Any]:
    data = {key: json.loads((data_dir / filename).read_text(encoding="utf-8")) for key, filename in FILES.items()}
    validate_data(data)
    asset_dir = data_dir.parent / "assets"
    if any(not (asset_dir / case["image"]).is_file() for case in data["crop_cases"]):
        raise DemoDataError("A crop case references a missing local illustration")
    return data
