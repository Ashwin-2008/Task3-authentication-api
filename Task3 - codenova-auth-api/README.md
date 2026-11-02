# CodeNova Task 3 — Authentication API

A RESTful authentication service built with FastAPI, SQLite, SQLAlchemy, Argon2 password hashing, and JWT access tokens.

## Features

- User registration with password complexity validation
- Secure Argon2 password hashing
- Login with signed JWT access tokens
- Protected user profile endpoint
- Configurable JWT expiration
- Environment-based configuration
- Consistent authentication error responses
- Automated tests using an isolated SQLite database
- OpenAPI documentation and Postman collection

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- PyJWT
- pwdlib with Argon2
- Pytest

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and replace the example JWT secret with a securely generated random secret.

Start the API:

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Obtain JWT |
| GET | `/api/v1/users/me` | Get authenticated user's profile |

## Password Requirements

Passwords must contain at least eight characters, an uppercase letter, a lowercase letter, a digit, and a special character.

## Authentication Flow

1. Register a user.
2. Log in using the registered email and password.
3. Copy the returned access token.
4. Send the token using `Authorization: Bearer <token>`.
5. Access the protected profile endpoint before the token expires.

## Run Tests

```bash
pytest
```

## Security

- Never store or log plaintext passwords.
- Never commit `.env` or actual credentials.
- Return HTTP 401 for missing, invalid, or expired access tokens.
- Do not expose password hashes in API responses.
- Use HTTPS when deploying outside localhost.
- Configure a strong secret and appropriate token lifetime.

## Project Structure

The application separates configuration, database access, models, schemas, routers, authentication services, and security utilities.

## License

Educational project developed for the CodeNova Backend Development Internship.
