from datetime import date
from uuid import uuid4

from flask_security import UserMixin
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.extensions import db


roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    fs_uniquifier = db.Column(
        db.String(64), unique=True, nullable=False, default=lambda: uuid4().hex
    )
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))
    accounts = db.relationship("Account", back_populates="user", cascade="all, delete-orphan")
    categories = db.relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = db.relationship("Budget", back_populates="user", cascade="all, delete-orphan")


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    balance = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    user = db.relationship("User", back_populates="accounts")
    transactions = db.relationship("Transaction", back_populates="account")

    __table_args__ = (
        CheckConstraint("type IN ('Checking', 'Savings', 'Cash', 'Credit')", name="ck_account_type"),
        CheckConstraint("balance <= 9999999999.99 AND balance >= -9999999999.99", name="ck_account_balance"),
    )


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    user = db.relationship("User", back_populates="categories")
    transactions = db.relationship("Transaction", back_populates="category")
    budgets = db.relationship("Budget", back_populates="category")

    __table_args__ = (
        CheckConstraint("type IN ('Income', 'Expense')", name="ck_category_type"),
        UniqueConstraint("user_id", "name", "type", name="uq_category_user_name_type"),
    )


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    notes = db.Column(db.String(500), nullable=False, default="")
    user = db.relationship("User", back_populates="transactions")
    account = db.relationship("Account", back_populates="transactions")
    category = db.relationship("Category", back_populates="transactions")

    __table_args__ = (
        CheckConstraint("type IN ('Income', 'Expense')", name="ck_transaction_type"),
        CheckConstraint("amount > 0 AND amount <= 9999999999.99", name="ck_transaction_amount"),
    )


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete="RESTRICT"), nullable=False, index=True)
    monthly_limit = db.Column(db.Numeric(12, 2), nullable=False)
    month_year = db.Column(db.String(7), nullable=False, index=True)
    user = db.relationship("User", back_populates="budgets")
    category = db.relationship("Category", back_populates="budgets")

    __table_args__ = (
        CheckConstraint("monthly_limit > 0 AND monthly_limit <= 9999999999.99", name="ck_budget_limit"),
        UniqueConstraint("user_id", "category_id", "month_year", name="uq_budget_user_category_month"),
    )