# Sponsorship CRM

Production-quality Sponsorship CRM for nonprofits, school clubs, and robotics teams.

## Stack
- Python 3.12 + Poetry
- FastAPI + SQLAlchemy + Alembic
- SQLite by default (PostgreSQL-ready URL-based config)
- React + TypeScript (Vite)
- APScheduler, Jinja2, BeautifulSoup4, Playwright
- Docker + GitHub Actions CI
- pytest + coverage gate (>90%)
- Ruff + Black formatting

## Features
- Organization discovery from public websites with robots.txt awareness
- Organization profile management
- Factual AI-style draft generation from templates
- Human review queue (approve/reject/decline/sent)
- Dashboard KPIs
- Audit log tracking
- CSV/Excel import and export

## Quick Start
See:
- `docs/installation.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/deployment.md`
- `docs/folder-structure.md`

## Local Development
### Backend
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Full stack with Docker
```bash
docker compose up --build
```
