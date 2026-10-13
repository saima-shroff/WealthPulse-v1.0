from datetime import date
from decimal import Decimal, InvalidOperation

from flask import abort, request


def json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="Request body must be a JSON object.")
    return data


def required_text(data, key, maximum, *, optional=False):
    value = data.get(key, "" if optional else None)
    if optional and value is None:
        return ""
    if not isinstance(value, str):
        abort(400, description=f"{key} must be text.")
    value = value.strip()
    if not value and optional:
        return ""
    if not value or len(value) > maximum:
        abort(400, description=f"{key} must contain 1 to {maximum} characters.")
    return value


def money(value, *, allow_zero=False):
    if isinstance(value, bool) or value is None:
        abort(400, description="Amount must be a valid monetary value.")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        abort(400, description="Amount must be a valid monetary value.")
    if not amount.is_finite() or amount > Decimal("9999999999.99"):
        abort(400, description="Amount is outside the supported range.")
    if amount != amount.quantize(Decimal("0.01")):
        abort(400, description="Amount can have at most two decimal places.")
    if amount < 0 or (amount == 0 and not allow_zero):
        abort(400, description="Amount must be positive.")
    return amount


def parse_date(value, key="date"):
    if not isinstance(value, str):
        abort(400, description=f"{key} must use YYYY-MM-DD format.")
    try:
        return date.fromisoformat(value)
    except ValueError:
        abort(400, description=f"{key} must use YYYY-MM-DD format.")


def as_money(value):
    return f"{value:.2f}"


def owned_record(model, record_id, user_id):
    record = model.query.filter_by(id=record_id, user_id=user_id).first()
    if record is None:
        abort(404, description="Resource not found.")
    return record