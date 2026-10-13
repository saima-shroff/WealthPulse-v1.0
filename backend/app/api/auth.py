import re

from flask import Blueprint, jsonify
from flask_security import hash_password, verify_password

from app.extensions import db
from app.models import User
from app.security import user_datastore
from app.api.common import json_body


bp = Blueprint("auth", __name__)
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def auth_response(user, status=200):
    return jsonify({"token": user.get_auth_token(), "user": {"id": user.id, "email": user.email}}), status


@bp.post("/register")
def register():
    data = json_body()
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email.strip()):
        return jsonify({"error": "Enter a valid email address."}), 400
    email = email.strip().lower()
    if len(email) > 255:
        return jsonify({"error": "Email address is too long."}), 400
    if not isinstance(password, str) or len(password) < 10 or len(password) > 128:
        return jsonify({"error": "Password must be between 10 and 128 characters."}), 400
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "An account with this email already exists."}), 409
    user = user_datastore.create_user(email=email, password=hash_password(password), active=True)
    db.session.commit()
    return auth_response(user, 201)


@bp.post("/login")
def login():
    data = json_body()
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Email and password are required."}), 400
    user = User.query.filter_by(email=email.strip().lower(), active=True).first()
    if user is None or not verify_password(password, user.password):
        return jsonify({"error": "Invalid email or password."}), 401
    return auth_response(user)