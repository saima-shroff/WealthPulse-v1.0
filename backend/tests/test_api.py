import pytest

from app import create_app
from app.extensions import db
from config import TestingConfig


@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.session.remove()
        db.drop_all()


def register(client, email):
    response = client.post("/api/auth/register", json={"email": email, "password": "long-enough-pass"})
    assert response.status_code == 201
    return response.get_json()["token"]


def headers(token):
    return {"Authentication-Token": token}


def test_token_auth_and_tenant_isolation(client):
    first_token = register(client, "one@example.com")
    second_token = register(client, "two@example.com")
    first = client.post("/api/accounts", headers=headers(first_token), json={"name": "Everyday", "type": "Checking", "balance": "100.00"})
    assert first.status_code == 201
    assert client.get("/api/accounts", headers=headers(second_token)).get_json() == []
    assert client.put(f"/api/accounts/{first.get_json()['id']}", headers=headers(second_token), json={"name": "Stolen"}).status_code == 404


def test_transaction_create_edit_delete_tracks_balance(client):
    token = register(client, "person@example.com")
    auth = headers(token)
    account = client.post("/api/accounts", headers=auth, json={"name": "Checking", "type": "Checking", "balance": "1000"}).get_json()
    category = client.post("/api/categories", headers=auth, json={"name": "Food", "type": "Expense"}).get_json()
    payload = {"account_id": account["id"], "category_id": category["id"], "amount": "25.50", "type": "Expense", "date": "2026-10-01", "notes": "Lunch"}
    created = client.post("/api/transactions", headers=auth, json=payload)
    assert created.status_code == 201
    assert client.get("/api/accounts", headers=auth).get_json()[0]["balance"] == "974.50"
    changed = {**payload, "amount": "40.00"}
    assert client.put(f"/api/transactions/{created.get_json()['id']}", headers=auth, json=changed).status_code == 200
    assert client.get("/api/accounts", headers=auth).get_json()[0]["balance"] == "960.00"
    assert client.delete(f"/api/transactions/{created.get_json()['id']}", headers=auth).status_code == 200
    assert client.get("/api/accounts", headers=auth).get_json()[0]["balance"] == "1000.00"


def test_transaction_rejects_another_users_account(client):
    first_token = register(client, "a@example.com")
    second_token = register(client, "b@example.com")
    account = client.post("/api/accounts", headers=headers(first_token), json={"name": "Checking", "type": "Checking"}).get_json()
    category = client.post("/api/categories", headers=headers(second_token), json={"name": "Food", "type": "Expense"}).get_json()
    response = client.post("/api/transactions", headers=headers(second_token), json={"account_id": account["id"], "category_id": category["id"], "amount": "10", "type": "Expense"})
    assert response.status_code == 400


def test_protected_endpoints_require_token(client):
    assert client.get("/api/accounts").status_code == 401
    assert client.get("/api/transactions").status_code == 401
    assert client.get("/api/budgets").status_code == 401


def test_budget_spending_and_transaction_date_filter(client):
    token = register(client, "budget@example.com")
    auth = headers(token)
    account = client.post("/api/accounts", headers=auth, json={"name": "Checking", "type": "Checking"}).get_json()
    category = client.post("/api/categories", headers=auth, json={"name": "Food", "type": "Expense"}).get_json()
    client.post("/api/transactions", headers=auth, json={
        "account_id": account["id"],
        "category_id": category["id"],
        "amount": "34.25",
        "type": "Expense",
        "date": "2026-10-08",
    })
    budget = client.post("/api/budgets", headers=auth, json={
        "category_id": category["id"],
        "monthly_limit": "200.00",
        "month_year": "2026-10",
    })
    assert budget.status_code == 201
    assert budget.get_json()["spent"] == "34.25"
    listed = client.get("/api/budgets?month=2026-10", headers=auth)
    assert listed.get_json()[0]["spent"] == "34.25"
    filtered = client.get("/api/transactions?start_date=2026-10-01&end_date=2026-10-31", headers=auth)
    assert filtered.get_json()["total"] == 1
    invalid = client.get("/api/transactions?start_date=not-a-date", headers=auth)
    assert invalid.status_code == 400


def test_registration_validates_password_and_duplicate_email(client):
    short_password = client.post("/api/auth/register", json={"email": "new@example.com", "password": "short"})
    assert short_password.status_code == 400
    register(client, "new@example.com")
    duplicate = client.post("/api/auth/register", json={"email": "new@example.com", "password": "long-enough-pass"})
    assert duplicate.status_code == 409