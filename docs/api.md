# API Documentation

Base URL: `/api/v1`

## Discovery
- `POST /discovery`
  - Body: `{ "urls": ["https://example.org"] }`
  - Returns discovered organizations.

## Organizations
- `GET /organizations`
- `POST /organizations`
- `PATCH /organizations/{organization_id}`

## Templates
- `GET /templates`
- `POST /templates`

## Draft Review Queue
- `GET /drafts`
- `POST /drafts`
- `PATCH /drafts/{draft_id}`
  - statuses: `pending`, `approved`, `rejected`, `declined`, `sent`

## Dashboard
- `GET /dashboard`

## Audit Logs
- `GET /audit-logs`

## Import / Export
- `POST /import-export/import/csv`
- `POST /import-export/import/excel`
- `GET /import-export/export/csv`
- `GET /import-export/export/excel`
