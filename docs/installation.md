# Installation Guide

## Prerequisites
- Python 3.12
- Poetry 2.x
- Node.js 20+
- npm 10+

## Backend Setup
```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables (backend)
- `ENVIRONMENT` (`development`, `testing`, `production`)
- `DB_SCHEME` (`sqlite+aiosqlite` or postgres driver)
- `DB_NAME`
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (for PostgreSQL)
- `CORS_ORIGINS` (JSON array)
