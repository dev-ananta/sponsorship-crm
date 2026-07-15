# Deployment Instructions

## Docker Compose (single host)
```bash
docker compose up --build -d
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Backend container notes
- Default DB is SQLite stored in docker volume `crm_db`.
- For PostgreSQL, set `DB_SCHEME`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.

## CI
GitHub Actions workflow (`.github/workflows/ci.yml`) runs:
- Backend lint checks (Ruff, Black)
- Backend tests with coverage gate
- Frontend build validation

## Production recommendations
- Run API behind reverse proxy (Nginx/Traefik)
- Move from SQLite to PostgreSQL
- Configure external object storage for imports/exports if needed
- Add SMTP integration only after explicit approved-draft send flow is wired
