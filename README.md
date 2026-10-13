# WealthPulse

## Project Overview

WealthPulse is a personal finance and budgeting dashboard built as a Vue 3 single-page application backed by a Flask REST API. It helps users understand account balances, track income and expenses, and plan category-based monthly spending using SQLAlchemy and SQLite.

## Features

* Register and sign in with token-based authentication and Argon2 password hashing.
* Manage checking, savings, cash, and credit accounts with balances updated by transactions.
* Create income and expense categories, with transaction filtering and pagination.
* Set monthly limits for expense categories and review spending against budgets.
* View responsive desktop and mobile layouts.

## Installation Steps

### Requirements
* Python 3.10 or newer
* Node.js 20 or newer and npm

### Local Setup
1. Clone the repository and configure environment files (`.env` for backend and `frontend/.env.local` for frontend).
2. Set up the Python virtual environment in the project root and install backend dependencies using `python -m pip install -r backend/requirements.txt`.
3. Navigate to the `frontend/` directory and run `npm ci`.
4. Start the Flask API in the `backend/` directory by running `python run.py` (listens on port 5000).
5. Start the Vite development server in the `frontend/` directory by running `npm run dev` (listens on port 5173).

## API Documentation

The API base URL is `http://127.0.0.1:5000`. Protected endpoints require the `Authentication-Token` header.

* `POST /api/auth/register` - Register an account and receive a token
* `POST /api/auth/login` - Authenticate and receive a token
* `GET`, `POST /api/accounts` - List or create accounts
* `PUT`, `DELETE /api/accounts/<id>` - Update or delete an account
* `GET`, `POST /api/categories` - List or create categories
* `GET`, `POST /api/transactions` - List or create transactions
* `PUT`, `DELETE /api/transactions/<id>` - Update or delete a transaction
* `GET`, `POST /api/budgets` - List current-month budgets or create one
* `GET /api/health` - Basic service health check