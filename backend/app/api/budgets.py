from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify
from flask_security import auth_required, current_user
from sqlalchemy import func

from app.api.common import as_money, json_body, money, parse_date
from app.extensions import db
from app.models import Budget, Category, Transaction


bp = Blueprint("budgets", __name__)


def budget_month(value):
    if value is None:
        return date.today().strftime("%Y-%m")
    if not isinstance(value, str) or len(value) != 7 or value[4] != "-":
        return None
    try:
        parse_date(f"{value}-01", "month_year")
    except Exception:
        return None
    return value


def serialize(item):
    start = date.fromisoformat(f"{item.month_year}-01")
    end = date(start.year + (start.month == 12), start.month % 12 + 1, 1)
    spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.category_id == item.category_id,
        Transaction.type == "Expense",
        Transaction.date >= start,
        Transaction.date < end,
    ).scalar()
    return {
        "id": item.id,
        "category_id": item.category_id,
        "category_name": item.category.name,
        "monthly_limit": as_money(item.monthly_limit),
        "month_year": item.month_year,
        "spent": as_money(Decimal(spent)),
    }


@bp.get("")
@auth_required("token")
def list_budgets():
    month = budget_month(__import__("flask").request.args.get("month"))
    if month is None:
        return jsonify({"error": "month must use YYYY-MM format."}), 400
    items = Budget.query.filter_by(user_id=current_user.id, month_year=month).all()
    return jsonify([serialize(item) for item in items])


@bp.post("")
@auth_required("token")
def create_budget():
    data = json_body()
    try:
        category_id = int(data.get("category_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Choose a valid expense category."}), 400
    category = Category.query.filter_by(id=category_id, user_id=current_user.id, type="Expense").first()
    if category is None:
        return jsonify({"error": "Choose a valid expense category."}), 400
    month = budget_month(data.get("month_year"))
    if month is None:
        return jsonify({"error": "month_year must use YYYY-MM format."}), 400
    if Budget.query.filter_by(user_id=current_user.id, category_id=category.id, month_year=month).first():
        return jsonify({"error": "A budget already exists for this category and month."}), 409
    try:
        limit = money(data.get("monthly_limit"))
    except Exception:
        return jsonify({"error": "monthly_limit must be a positive monetary value."}), 400
    item = Budget(user_id=current_user.id, category=category, monthly_limit=limit, month_year=month)
    db.session.add(item)
    db.session.commit()
    return jsonify(serialize(item)), 201