---
name: python-fastapi-mastery
description: "Build Python APIs with FastAPI, Pydantic v2, and SQLAlchemy 2.0. Covers project structure, async patterns, JWT authentication, validation, and database integration with uv package manager."
category: modernization
metadata:
  triggers: [creating Python APIs, setting up FastAPI projects, implementing JWT auth, configuring SQLAlchemy async, troubleshooting 422, CORS, async blocking]
  stack: [FastAPI 0.123.2, Pydantic 2.11.7, SQLAlchemy 2.0.30, Uvicorn 0.35.0, python-jose 3.3.0, uv]
---

# FastAPI & Python Industrial Mastery (v21.0)
Production-tested patterns for FastAPI with Pydantic v2, SQLAlchemy 2.0 async, and JWT authentication.

###  Latest Versions (Verified Dec 2025)
- **FastAPI**: 0.123.2
- **Pydantic**: 2.11.7
- **SQLAlchemy**: 2.0.30
- **Uvicorn**: 0.35.0
- **python-jose**: 3.3.0

##  Quick Start (uv toolchain)
```bash
# Create project
uv init my-api && cd my-api
# Add dependencies
uv add fastapi[standard] sqlalchemy[asyncio] aiosqlite python-jose[cryptography] passlib[bcrypt]
# Run development server
uv run fastapi dev src/main.py
```

##  Domain-Based Project Structure
```text
my-api/
├── pyproject.toml
├── src/
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Global settings
│   ├── database.py          # Database connection
│   ├── {domain}/            # e.g., auth, items
│   │   ├── router.py        # Domain endpoints
│   │   ├── schemas.py       # Pydantic models
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── service.py       # Business logic
│   │   └── dependencies.py  # Domain dependencies
│   └── shared/              # Shared utilities
└── tests/                   # Pytest suites
```

##  Core Patterns

### 1. Pydantic v2 schemas
- **Rule**: Use `Field()` for validation constraints.
- **Rule**: Separate Create/Update/Response schemas.
- **Rule**: Use `model_config = ConfigDict(from_attributes=True)`.

### 2. SQLAlchemy 2.0 Async
- **Rule**: Use `Mapped` and `mapped_column` type annotations.
- **Rule**: Yield session via `async_session()`.

### 3. JWT Authentication
- **Rule**: Implement `OAuth2PasswordBearer` and `decode_token` orchestration.

##  Critical Rules

###  ALWAYS DO
- Separate Pydantic schemas from SQLAlchemy models.
- Use `async` for all I/O operations (DB, HTTP).
- Use dependency injection (`Depends()`) for DB and Auth.

###  NEVER DO
- Never use blocking calls like `time.sleep()` in async routes.
- Never put business logic in routes; use the Service layer.
- Never hardcode secrets; use `pydantic-settings`.

##  Industrial Troubleshooting
- **422 Validation**: Use a custom `RequestValidationError` handler to return body context.
- **CORS**: Explicitly define `allow_origins` for production safety.
- **Async Blocking**: If all requests hang, search for `sync` calls in `async` routes.
