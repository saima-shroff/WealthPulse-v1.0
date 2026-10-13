# WealthPulse

## Project Overview

WealthPulse is a personal finance and budgeting dashboard built as a Vue 3 single-page application backed by a Flask REST API[cite: 1]. It helps users understand account balances, track income and expenses, and plan category-based monthly spending using SQLAlchemy and SQLite[cite: 1].

## Features

* Register and sign in with token-based authentication and Argon2 password hashing[cite: 1].
* Manage checking, savings, cash, and credit accounts with balances updated by transactions[cite: 1].
* Create income and expense categories, with transaction filtering and pagination[cite: 1].
* Set monthly limits for expense categories and review spending against budgets[cite: 1].
* View responsive desktop and mobile layouts[cite: 1].

## Installation Steps

### Requirements
* Python 3.10 or newer[cite: 1]
* Node.js 20 or newer and npm[cite: 1]

### Local Setup
1. Clone the repository and configure environment files (`.env` for backend and `frontend/.env.local` for frontend)[cite: 1].
2. Set up the Python virtual environment in the project root and install backend dependencies using `python -m pip install -r backend/requirements.txt`[cite: 1].
3. Navigate to the `frontend/` directory and run `npm ci`[cite: 1].
4. Start the Flask API in the `backend/` directory by running `python run.py` (listens on port 5000)[cite: 1].
5. Start the Vite development server in the `frontend/` directory by running `npm run dev` (listens on port 5173)[cite: 1].

## API Documentation

The API base URL is `http://127.0.0.1:5000`[cite: 1]. Protected endpoints require the `Authentication-Token` header[cite: 1].

* `POST /api/auth/register` - Register an account and receive a token[cite: 1]
* `POST /api/auth/login` - Authenticate and receive a token[cite: 1]
* `GET`, `POST /api/accounts` - List or create accounts[cite: 1]
* `PUT`, `DELETE /api/accounts/<id>` - Update or delete an account[cite: 1]
* `GET`, `POST /api/categories` - List or create categories[cite: 1]
* `GET`, `POST /api/transactions` - List or create transactions[cite: 1]
* `PUT`, `DELETE /api/transactions/<id>` - Update or delete a transaction[cite: 1]
* `GET`, `POST /api/budgets` - List current-month budgets or create one[cite: 1]
* `GET /api/health` - Basic service health check[cite: 1]