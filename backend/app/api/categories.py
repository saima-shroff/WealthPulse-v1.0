from flask import Blueprint, jsonify
from flask_security import auth_required, current_user

from app.api.common import json_body, required_text
from app.extensions import db
from app.models import Category


bp = Blueprint("categories", __name__)
CATEGORY_TYPES = {"Income", "Expense"}


@bp.get("")
@auth_required("token")
def list_categories():
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.type, Category.name).all()
    return jsonify([{"id": item.id, "name": item.name, "type": item.type} for item in categories])


@bp.post("")
@auth_required("token")
def create_category():
    data = json_body()
    category_type = data.get("type")
    if category_type not in CATEGORY_TYPES:
        return jsonify({"error": "Category type must be Income or Expense."}), 400
    name = required_text(data, "name", 80)
    if Category.query.filter_by(user_id=current_user.id, name=name, type=category_type).first():
        return jsonify({"error": "This category already exists."}), 409
    category = Category(user_id=current_user.id, name=name, type=category_type)
    db.session.add(category)
    db.session.commit()
    return jsonify({"id": category.id, "name": category.name, "type": category.type}), 201