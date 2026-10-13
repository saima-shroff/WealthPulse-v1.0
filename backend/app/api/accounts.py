from flask import Blueprint, jsonify
from flask_security import auth_required, current_user

from app.api.common import as_money, json_body, money, owned_record, required_text
from app.extensions import db
from app.models import Account, Transaction


bp = Blueprint("accounts", __name__)
ACCOUNT_TYPES = {"Checking", "Savings", "Cash", "Credit"}


def serialize(account):
    return {"id": account.id, "name": account.name, "type": account.type, "balance": as_money(account.balance)}


@bp.get("")
@auth_required("token")
def list_accounts():
    accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.name).all()
    return jsonify([serialize(account) for account in accounts])


@bp.post("")
@auth_required("token")
def create_account():
    data = json_body()
    account_type = data.get("type")
    if account_type not in ACCOUNT_TYPES:
        return jsonify({"error": "Choose a valid account type."}), 400
    account = Account(
        user_id=current_user.id,
        name=required_text(data, "name", 80),
        type=account_type,
        balance=money(data.get("balance", 0), allow_zero=True),
    )
    db.session.add(account)
    db.session.commit()
    return jsonify(serialize(account)), 201


@bp.put("/<int:account_id>")
@auth_required("token")
def update_account(account_id):
    account = owned_record(Account, account_id, current_user.id)
    data = json_body()
    account_type = data.get("type", account.type)
    if account_type not in ACCOUNT_TYPES:
        return jsonify({"error": "Choose a valid account type."}), 400
    account.name = required_text(data, "name", 80) if "name" in data else account.name
    account.type = account_type
    if "balance" in data:
        if Transaction.query.filter_by(user_id=current_user.id, account_id=account.id).first():
            return jsonify({"error": "Account balance is maintained by its transactions."}), 409
        account.balance = money(data["balance"], allow_zero=True)
    db.session.commit()
    return jsonify(serialize(account))


@bp.delete("/<int:account_id>")
@auth_required("token")
def delete_account(account_id):
    account = owned_record(Account, account_id, current_user.id)
    if Transaction.query.filter_by(user_id=current_user.id, account_id=account.id).first():
        return jsonify({"error": "Remove this account's transactions before deleting it."}), 409
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Account deleted."})