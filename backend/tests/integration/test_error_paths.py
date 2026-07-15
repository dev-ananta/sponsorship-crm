import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_duplicate_organization_returns_conflict(client: AsyncClient) -> None:
    payload = {"name": "Org", "website": "https://org.org"}
    first = await client.post("/api/v1/organizations", json=payload)
    second = await client.post("/api/v1/organizations", json=payload)

    assert first.status_code == 200
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_review_missing_draft_returns_not_found(client: AsyncClient) -> None:
    response = await client.patch(
        "/api/v1/drafts/999",
        json={"status": "approved"},
    )

    assert response.status_code == 404
