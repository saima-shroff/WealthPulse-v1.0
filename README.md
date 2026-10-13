# WealthPulse

## Project overview

WealthPulse is a personal finance and budgeting dashboard built as a Vue 3 single-page application backed by a Flask REST API. It helps users understand account balances, track income and expenses, and plan category-based monthly spending. SQLAlchemy provides access to a SQLite development database.

The project is split into `backend/` for the API and `frontend/` for the web application. By default, the API listens on port `5000`, and Vite serves the frontend on port `5173`.

## Features

- Register and sign in with expiring authentication tokens; passwords are hashed with Argon2.
- Manage checking, savings, cash, and credit accounts, with balances updated by transaction activity.
- Create income and expense categories, then filter and paginate transactions by date, account, or category.
- Set monthly limits for expense categories and review spending against each budget.
- View net worth, monthly income and expenses, cash flow, spending categories, and recent activity.
- Use responsive desktop and mobile layouts with protected frontend routes.

## Installation steps

### Requirements

- Python 3.10 or newer
- Node.js 20 or newer and npm

## Local setup

### Clone the repository

After creating the public repository, clone it with its GitHub URL. Replace `<OWNER>` with the GitHub account or organization that owns it:

```sh
git clone https://github.com/<OWNER>/WealthPulse.git
cd WealthPulse
```

If you are already in a local checkout, continue to the next step.

### Create the Python environment

Use Python 3.10 or newer. On Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Then, from the repository root on any platform:

```sh
python -m pip install -r backend/requirements.txt
```

### Configure local environment

The root `.env.example` contains Flask settings. Copy it to `.env` in the repository root.

```powershell
Copy-Item .env.example .env
```

```sh
cp .env.example .env
```

The frontend has its own `frontend/.env.example`. Copy it to `frontend/.env.local` so Vite can load `VITE_API_URL`:

```powershell
Copy-Item frontend/.env.example frontend/.env.local
```

```sh
cp frontend/.env.example frontend/.env.local
```

The example values are only for local development. Before deploying, set unique, randomly generated `SECRET_KEY` and `SECURITY_PASSWORD_SALT` values in `.env`; never commit either `.env` file. For example, run `python -c "import secrets; print(secrets.token_urlsafe(48))"` twice and use the two outputs for the values.

### Start the application

Start the Flask API in terminal one, from the repository root:

```sh
cd backend
python run.py
```

The API listens at `http://127.0.0.1:5000`. SQLite creates its database in Flask's `backend/instance/` directory on first start.

In terminal two, from the repository root, install from the lockfile and start Vite:

```sh
cd frontend
npm ci
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`. Register an account, then add a financial account and an expense category before recording expenses. Budgets are configured for expense categories.

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `APP_ENV` | `development`, `testing`, or `production` | `development` |
| `SECRET_KEY` | Flask signing key | Development-only value |
| `SECURITY_PASSWORD_SALT` | Flask-Security token salt | Development-only fallback |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///wealthpulse.db` |
| `FRONTEND_ORIGIN` | Allowed browser origin for API CORS | `http://localhost:5173` |
| `VITE_API_URL` | Frontend API base URL; set in `frontend/.env.local` | `http://127.0.0.1:5000/api` |

Production startup refuses to use missing signing secrets. Use HTTPS in production, set a strong unique secret and password salt, configure `DATABASE_URL` for a durable database, and set `FRONTEND_ORIGIN` to the deployed frontend origin. The included SQLite setup is intended for local development, not multi-worker production deployments.

## API documentation

The API base URL is `http://127.0.0.1:5000`. All endpoints return JSON. Registration and login return a token and user summary. Send the token in the `Authentication-Token` header on every protected route:

```http
Authentication-Token: <token>
```

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Create an account and receive a token |
| `POST` | `/api/auth/login` | Authenticate and receive a token |
| `GET`, `POST` | `/api/accounts` | List or create accounts |
| `PUT`, `DELETE` | `/api/accounts/<id>` | Update or delete an account |
| `GET`, `POST` | `/api/categories` | List or create categories |
| `GET`, `POST` | `/api/transactions` | List or create transactions |
| `PUT`, `DELETE` | `/api/transactions/<id>` | Update or delete a transaction |
| `GET`, `POST` | `/api/budgets` | List current-month budgets or create one |
| `GET` | `/api/health` | Basic service health check |

### Request fields

All request bodies use JSON. IDs supplied for related records must belong to the authenticated user.

| Resource | Fields and validation |
| --- | --- |
| Account | `name` is required (1–80 characters); `type` is `Checking`, `Savings`, `Cash`, or `Credit`; `balance` is optional on creation and defaults to zero. Balance cannot be edited once transactions exist. |
| Category | `name` is required (1–80 characters); `type` is `Income` or `Expense`. A user cannot create a duplicate name/type pair. |
| Transaction | `account_id`, `category_id`, and positive `amount` are required. `type` is `Income` or `Expense`, defaults to the category type, and must match the category. `date` is optional (`YYYY-MM-DD`, defaults to today); `notes` is optional (up to 500 characters). |
| Budget | `category_id` must be the user's expense category; `monthly_limit` must be positive; `month_year` is optional (`YYYY-MM`, defaults to the current month). Only one budget per category/month is allowed. |

Money values allow at most two decimal places. Transaction amounts are positive; the transaction type determines whether that amount increases or decreases the account balance.

### Example requests

Register. Passwords must contain 10–128 characters. Successful registration returns `201 Created` with the same response structure as login.

```http
POST /api/auth/register
Content-Type: application/json

{"email":"alex@example.com","password":"a-long-unique-password"}
```

Login returns an authentication token and user summary:

```json
{"token":"<authentication-token>","user":{"id":1,"email":"alex@example.com"}}
```

Create an account and an expense category before recording expenses:

```http
POST /api/accounts
Authentication-Token: <token>
Content-Type: application/json

{"name":"Everyday checking","type":"Checking","balance":"1250.00"}
```

```http
POST /api/categories
Authentication-Token: <token>
Content-Type: application/json

{"name":"Groceries","type":"Expense"}
```

Create a transaction:

```http
POST /api/transactions
Authentication-Token: <token>
Content-Type: application/json

{"account_id":1,"category_id":2,"amount":"24.50","type":"Expense","date":"2026-10-13","notes":"Lunch"}
```

Create a monthly budget:

```http
POST /api/budgets
Authentication-Token: <token>
Content-Type: application/json

{"category_id":2,"monthly_limit":"400.00","month_year":"2026-10"}
```

### Filtering and pagination

`GET /api/transactions` accepts optional `start_date`, `end_date`, `category_id`, and `account_id` filters. Dates use `YYYY-MM-DD`. Pagination uses `page` (default `1`) and `per_page` (default `20`, maximum `100`). The response contains `items`, `page`, `per_page`, `total`, and `pages`.

`GET /api/budgets` accepts optional `month=YYYY-MM` and defaults to the current month. Budget results include category name, monthly limit, month, and the category's expense total for that month.

Example: `GET /api/transactions?start_date=2026-10-01&end_date=2026-10-31&page=1&per_page=20`.

### Errors

Error responses use JSON, for example `{"error":"Authentication required."}`.

| Status | Meaning |
| --- | --- |
| `400 Bad Request` | Invalid JSON, field, date, filter, or related resource ID |
| `401 Unauthorized` | Missing, invalid, or expired token |
| `404 Not Found` | Resource is missing or not owned by the authenticated user |
| `409 Conflict` | Duplicate category/budget, or an account is still referenced by transactions |

## Security and data behavior

- Passwords use Flask-Security's Argon2 hashing; tokens expire after seven days.
- Every finance query is scoped to the authenticated user. Related account/category IDs are checked against that same user, and inaccessible record IDs return `404`.
- Monetary fields use decimal database columns, positive transaction amounts, and two-decimal precision. Account balances are adjusted transactionally when ledger entries are created, edited, or deleted.
- SQLAlchemy enables SQLite foreign-key enforcement. API inputs receive type, range, enum, date, length, and ownership validation.
- Registration does not send email. Email verification, password reset, rate limiting, and migration tooling are not included in this development build and should be added before a public deployment.

## Tests and production build

With the Python virtual environment activated, run the backend tests from the backend directory:

```sh
cd backend
python -m pytest -q
```

Run a clean frontend install and production build from the frontend directory:

```sh
cd frontend
npm ci
npm run build
```

## GitHub Actions

The workflow in `.github/workflows/ci.yml` runs on pushes, pull requests, and manual dispatch. It runs backend tests on Python 3.10 and 3.12, and installs the frontend from `package-lock.json` before building with Node.js 20.

## Publish to GitHub

1. On GitHub, create a **public** repository named `WealthPulse`. Leave the options to add a README, `.gitignore`, or license unchecked because those files are already in this project.
2. From this project directory, initialize Git and review the staged files before committing:

	```sh
	git init -b main
	git add .
	git status --short
	git diff --cached --stat
	```

	Confirm that `.env`, `.env.local`, `.venv/`, `backend/instance/`, `frontend/node_modules/`, and database files are not staged. Review the staged files for personal data or secrets before continuing.

3. Commit and push. Replace `<OWNER>` with the GitHub account or organization name:

	```sh
	git commit -m "Initial WealthPulse release"
	git remote add origin https://github.com/<OWNER>/WealthPulse.git
	git push -u origin main
	```

4. After the first push, confirm the GitHub Actions checks pass. Consider enabling private vulnerability reporting and branch protection in repository settings.

## License

No license has been selected or included. A public repository can be viewed, but public visibility alone does not grant permission to reuse, modify, or redistribute the code. Choose and add a `LICENSE` file before inviting contributions or granting reuse rights.

See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.