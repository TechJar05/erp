from uuid import UUID
from datetime import datetime, date

def make_json_safe(obj):
    if isinstance(obj, dict):
        return {
            str(k): make_json_safe(v)   # 🔥 convert KEYS too
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [make_json_safe(i) for i in obj]

    if isinstance(obj, tuple):
        return [make_json_safe(i) for i in obj]

    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    return obj
