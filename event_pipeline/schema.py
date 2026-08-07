import json
from pathlib import Path

import jsonschema

# تحديد المسار إلى ملف الـ schema المتفق عليه
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "docs" / "event_schema.json"

with open(SCHEMA_PATH, encoding="utf-8") as f:
    EVENT_SCHEMA = json.load(f)


def validate_event(event: dict) -> None:
    """ترفع استثناء jsonschema.ValidationError إذا كان الحدث مخالفاً للعقد"""
    jsonschema.validate(instance=event, schema=EVENT_SCHEMA)