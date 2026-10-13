from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException

from app.api.accounts import bp as accounts_bp
from app.api.auth import bp as auth_bp
from app.api.budgets import bp as budgets_bp
from app.api.categories import bp as categories_bp
from app.api.transactions import bp as transactions_bp


api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(auth_bp, url_prefix="/auth")
api.register_blueprint(accounts_bp, url_prefix="/accounts")
api.register_blueprint(categories_bp, url_prefix="/categories")
api.register_blueprint(transactions_bp, url_prefix="/transactions")
api.register_blueprint(budgets_bp, url_prefix="/budgets")


@api.errorhandler(HTTPException)
def handle_http_error(error):
    return jsonify({"error": error.description}), error.code