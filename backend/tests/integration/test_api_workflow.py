import io

import pandas as pd
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_organization_template_draft_flow(client: AsyncClient) -> None:
    create_org = await client.post(
        "/api/v1/organizations",
        json={
            "name": "STEM Booster",
            "website": "https://stembooster.org",
            "mission": "Support local STEM teams",
            "description": "Community nonprofit",
            "industry": "Nonprofit",
            "location": "Austin",
            "public_email": "sponsor@stembooster.org",
            "public_contact": "Sponsorship Desk",
            "notes": "Met at event",
        },
    )
    assert create_org.status_code == 200
    org_id = create_org.json()["id"]

    create_template = await client.post(
        "/api/v1/templates",
        json={
            "name": "base-template",
            "subject_blueprint": "Support {{organization}}",
            "body_blueprint": "Mission {{mission}} Event {{event}} Request {{request}}",
        },
    )
    assert create_template.status_code == 200
    template_id = create_template.json()["id"]

    create_draft = await client.post(
        "/api/v1/drafts",
        json={
            "organization_id": org_id,
            "template_id": template_id,
            "sender_name": "Taylor",
            "event": "Robotics invitational",
            "request": "$250 support",
        },
    )
    assert create_draft.status_code == 200
    draft_id = create_draft.json()["id"]

    review = await client.patch(
        f"/api/v1/drafts/{draft_id}",
        json={"status": "approved"},
    )
    assert review.status_code == 200
    assert review.json()["status"] == "approved"


@pytest.mark.asyncio
async def test_dashboard_and_audit_logs(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/organizations",
        json={"name": "Alpha", "website": "https://alpha.org"},
    )

    dashboard = await client.get("/api/v1/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["organizations_imported"] == 1

    logs = await client.get("/api/v1/audit-logs")
    assert logs.status_code == 200
    assert len(logs.json()) >= 1


@pytest.mark.asyncio
async def test_import_and_export_csv(client: AsyncClient) -> None:
    data = pd.DataFrame(
        [
            {"name": "Org One", "website": "https://org-one.org"},
            {"name": "Org Two", "website": "https://org-two.org"},
        ]
    )
    buffer = io.StringIO()
    data.to_csv(buffer, index=False)

    files = {"file": ("orgs.csv", buffer.getvalue(), "text/csv")}
    imported = await client.post("/api/v1/import-export/import/csv", files=files)
    assert imported.status_code == 200
    assert imported.json()["imported"] == 2

    exported = await client.get("/api/v1/import-export/export/csv")
    assert exported.status_code == 200
    assert "organizations.csv" in exported.headers.get("content-disposition", "")
    assert "Org One" in exported.text


@pytest.mark.asyncio
async def test_import_excel(client: AsyncClient) -> None:
    frame = pd.DataFrame([{"name": "Org X", "website": "https://orgx.org"}])
    output = io.BytesIO()
    frame.to_excel(output, index=False)

    files = {
        "file": (
            "orgs.xlsx",
            output.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    imported = await client.post("/api/v1/import-export/import/excel", files=files)

    assert imported.status_code == 200
    assert imported.json()["imported"] == 1
