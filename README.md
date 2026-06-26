# 💰 Finance Tracker API

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![pytest](https://img.shields.io/badge/tested%20with-pytest-yellow)

A personal finance management API built with FastAPI and SQLAlchemy to manage a PostgreSQL database.

## 🚀 Features

+ 🔐 JWT authentication
+ 👤 User registration and management
+ 📂 Category management (CRUD operations)
+ 💸 Transaction management (CRUD operations)
+ 📊 Budget management (CRUD operations)
+ 🛡️ Data isolation — users can only access their own data

## 🛠️ Tech Stack

+ **Python 3.12**
+ **FastAPI 0.136**
+ **SQLAlchemy 2.0**
+ **PostgreSQL 16**
+ **Alembic**
+ **Docker**
+ **JWT (python-jose)**
+ **pytest**

## ✅ Requirements

+ Python 3.12+
+ PostgreSQL 16+
+ Docker & Docker Compose (for Docker setup)

## 🗂️ Project Structure

```
finance-tracker-api/
├── app/
│   ├── api/
│   │   ├── endpoints/      # Route handlers
│   │   └── dependencies.py # FastAPI dependencies
│   ├── core/               # Config and database
│   ├── exceptions/         # Custom exceptions
│   ├── models/             # SQLAlchemy ORM models
│   ├── repositories/       # Database queries
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── utils/              # JWT and security
│   └── main.py
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/                # Database migrations
├── docs/
│   └── db_schema.png
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🗄️ Database Schema

![DB Schema](docs/db/db_schema.png)

## 🛠️ Installing / Getting started

### 1. 📥 Clone project from GitHub to local computer

Open the terminal in the directory where you want to place the project and run:

```bash
git clone git@github.com:dmytrominyaylo/finance-tracker-api.git
```

### 2. 🐍 Create and activate virtual environment

```bash
python -m venv .venv
```

To activate virtualenv:

a) On macOS/Linux:
```bash
source .venv/bin/activate
```

b) On Windows:
```bash
.venv\Scripts\activate
```

### 3. 📦 Install project dependencies

```bash
pip install -r requirements.txt
```

### 4. ⚙️ Create a .env file

Rename `.env.example` file to `.env`. Open it and fill in all variables with your configuration settings.

### 5. 🐳 Run project with Docker

The project is Dockerized for easy setup. Migrations run automatically on startup.

```bash
docker-compose up --build
```

### 6. 🖥️ Run project locally

Apply migrations:
```bash
alembic upgrade head
```

Start FastAPI app:
```bash
uvicorn app.main:app --reload
```

## 📖 API Documentation

After starting the server, open Swagger UI:

```
http://localhost:8000/docs
```

## 🧪 Testing the API

1. Register a new user via `POST /api/users/`
2. Login via `POST /api/auth/login` to get an access token
3. Click the **Authorize** 🔒 button in Swagger UI
4. Enter the token in the format: `Bearer your_token_here`
5. Now all protected endpoints are available

## 🧬 Running Tests

```bash
pytest
```

Or with verbose output:
```bash
pytest -v
```

## 👤 Author

**Dmytro Minyaylo**
+ GitHub: [@dmytrominyaylo](https://github.com/dmytrominyaylo)