from datetime import date

from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user

from app.api.common import as_money, json_body, money, owned_record, parse_date, required_text
from app.extensions import db
from app.models import Account, Category, Transaction


bp = Blueprint("transactions", __name__)
TRANSACTION_TYPES = {"Income", "Expense"}


def serialize(item):
    return {
        "id": item.id,
        "account_id": item.account_id,
        "account_name": item.account.name,
        "category_id": item.category_id,
        "category_name": item.category.name,
        "amount": as_money(item.amount),
        "type": item.type,
        "date": item.date.isoformat(),
        "notes": item.notes,
    }


def apply_balance(account, item_type, amount, reverse=False):
    sign = 1 if item_type == "Income" else -1
    account.balance += amount * sign * (-1 if reverse else 1)


def validated_relations(data, user_id, fallback=None):
    account_id = data.get("account_id", fallback.account_id if fallback else None)
    category_id = data.get("category_id", fallback.category_id if fallback else None)
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if account is None or category is None:
        return None, None, ("Choose an account and category that belong to your profile.", 400)
    item_type = data.get("type", fallback.type if fallback else category.type)
    if item_type not in TRANSACTION_TYPES or category.type != item_type:
        return None, None, ("Transaction type must match the category type.", 400)
    return (account, category, item_type), None, None


def build_transaction(data, user_id, fallback=None):
    relations, _, error = validated_relations(data, user_id, fallback)
    if error:
        return None, error
    account, category, item_type = relations
    try:
        amount = money(data["amount"] if "amount" in data else fallback.amount)
        transaction_date = parse_date(data["date"]) if "date" in data else (fallback.date if fallback else date.today())
        notes = required_text(data, "notes", 500, optional=True) if "notes" in data else (fallback.notes if fallback else "")
    except KeyError:
        return None, ("Amount is required.", 400)
    return {
        "account": account,
        "category": category,
        "amount": amount,
        "type": item_type,
        "date": transaction_date,
        "notes": notes,
    }, None


@bp.get("")
@auth_required("token")
def list_transactions():
    query = Transaction.query.filter_by(user_id=current_user.id)
    if request.args.get("start_date"):
        query = query.filter(Transaction.date >= parse_date(request.args["start_date"], "start_date"))
    if request.args.get("end_date"):
        query = query.filter(Transaction.date <= parse_date(request.args["end_date"], "end_date"))
    for parameter, column in (("category_id", Transaction.category_id), ("account_id", Transaction.account_id)):
        if request.args.get(parameter):
            try:
                identifier = int(request.args[parameter])
            except ValueError:
                return jsonify({"error": f"{parameter} must be an integer."}), 400
            query = query.filter(column == identifier)
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
    except ValueError:
        return jsonify({"error": "page and per_page must be integers."}), 400
    pagination = query.order_by(Transaction.date.desc(), Transaction.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [serialize(item) for item in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    })


@bp.post("")
@auth_required("token")
def create_transaction():
    values, error = build_transaction(json_body(), current_user.id)
    if error:
        return jsonify({"error": error[0]}), error[1]
    item = Transaction(user_id=current_user.id, **values)
    apply_balance(item.account, item.type, item.amount)
    db.session.add(item)
    db.session.commit()
    return jsonify(serialize(item)), 201


@bp.put("/<int:transaction_id>")
@auth_required("token")
def update_transaction(transaction_id):
    existing = owned_record(Transaction, transaction_id, current_user.id)
    replacement, error = build_transaction(json_body(), current_user.id, existing)
    if error:
        return jsonify({"error": error[0]}), error[1]
    apply_balance(existing.account, existing.type, existing.amount, reverse=True)
    apply_balance(replacement["account"], replacement["type"], replacement["amount"])
    existing.account = replacement["account"]
    existing.category = replacement["category"]
    existing.amount = replacement["amount"]
    existing.type = replacement["type"]
    existing.date = replacement["date"]
    existing.notes = replacement["notes"]
    db.session.commit()
    return jsonify(serialize(existing))


@bp.delete("/<int:transaction_id>")
@auth_required("token")
def delete_transaction(transaction_id):
    item = owned_record(Transaction, transaction_id, current_user.id)
    apply_balance(item.account, item.type, item.amount, reverse=True)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Transaction deleted."})