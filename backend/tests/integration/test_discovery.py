import pytest
from httpx import AsyncClient

from app.services.crawler import ComplianceScraper


@pytest.mark.asyncio
async def test_discovery_endpoint_imports_profiles(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_extract_profile(_: ComplianceScraper, url: str) -> dict[str, str | None]:
        return {
            "name": "Discovered Org",
            "website": url,
            "mission": "Mission data",
            "description": "Description",
            "industry": "Education",
            "location": "Seattle",
            "public_email": "hello@discovered.org",
            "public_contact": "Contact Team",
            "notes": "Public website",
        }

    monkeypatch.setattr(ComplianceScraper, "extract_profile", fake_extract_profile)

    response = await client.post(
        "/api/v1/discovery",
        json={"urls": ["https://discover-me.org"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Discovered Org"
