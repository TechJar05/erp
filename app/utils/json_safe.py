from datetime import datetime
from uuid import UUID
from decimal import Decimal
from sqlalchemy.engine import RowMapping

def make_json_safe(obj):
    if isinstance(obj, list):
        return [make_json_safe(i) for i in obj]

    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}

    if isinstance(obj, RowMapping):
        return dict(obj)

    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, datetime):
        return obj.isoformat()

    return obj
