import pytest

from app.services.crawler import ComplianceScraper


@pytest.mark.asyncio
async def test_extract_profile_parses_public_information(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html>
      <head><title>Example Foundation</title></head>
      <body>
        <h2>Mission</h2>
        <p>Mission: empower students through technology.</p>
        <p>Location: Boston, MA</p>
        <a href="mailto:hello@example.org">Email</a>
      </body>
    </html>
    """

    scraper = ComplianceScraper()

    monkeypatch.setattr(scraper, "_robots_allowed", lambda _: True)

    async def fake_fetch(_: str) -> str:
        return html

    monkeypatch.setattr(scraper, "_fetch_html", fake_fetch)
    monkeypatch.setattr(scraper, "_candidate_links", lambda _url, _soup: [])

    profile = await scraper.extract_profile("https://example.org")

    assert profile["name"] == "Example Foundation"
    assert profile["mission"] == "Mission"
    assert profile["location"] == "Location: Boston, MA"
    assert profile["public_email"] == "hello@example.org"


@pytest.mark.asyncio
async def test_extract_profile_blocks_robots(monkeypatch: pytest.MonkeyPatch) -> None:
    scraper = ComplianceScraper()
    monkeypatch.setattr(scraper, "_robots_allowed", lambda _: False)

    with pytest.raises(Exception):
        await scraper.extract_profile("https://example.org")
