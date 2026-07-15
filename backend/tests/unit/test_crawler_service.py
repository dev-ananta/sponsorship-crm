import pytest
from bs4 import BeautifulSoup

from app.services.crawler import ComplianceScraper


@pytest.mark.asyncio
async def test_extract_profile_parses_public_information(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


@pytest.mark.asyncio
async def test_extract_profile_uses_playwright_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    html = "<html><head><title>Fallback Org</title></head><body><p>Mission text</p></body></html>"
    scraper = ComplianceScraper()
    monkeypatch.setattr(scraper, "_robots_allowed", lambda _: True)

    async def fail_fetch(_: str) -> str:
        raise RuntimeError("network")

    async def fallback_fetch(_: str) -> str:
        return html

    monkeypatch.setattr(scraper, "_fetch_html", fail_fetch)
    monkeypatch.setattr(scraper, "_fetch_html_with_playwright", fallback_fetch)
    monkeypatch.setattr(scraper, "_candidate_links", lambda _url, _soup: [])

    profile = await scraper.extract_profile("https://fallback.org")
    assert profile["name"] == "Fallback Org"


def test_candidate_links_and_contact_parsing() -> None:
    scraper = ComplianceScraper()
    soup = BeautifulSoup(
        """
        <html>
            <body>
                <a href="/about">About</a>
                <a href="https://example.org/contact">Contact</a>
                <a href="https://other.org/about">Other</a>
                <a href="mailto:person@example.org">Reach us</a>
            </body>
        </html>
        """,
        "html.parser",
    )
    links = scraper._candidate_links("https://example.org", soup)
    assert "https://example.org/about" in links
    assert "https://example.org/contact" in links

    email, contact = scraper._extract_contact(soup)
    assert email == "person@example.org"
    assert contact == "Contact"


def test_robots_allowed_happy_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    scraper = ComplianceScraper()

    class DummyResponse:
        def __init__(self, status_code: int, text: str) -> None:
            self.status_code = status_code
            self.text = text

    class DummyClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self) -> "DummyClient":
            return self

        def __exit__(self, *args) -> None:
            return None

        def get(self, _url: str) -> DummyResponse:
            return DummyResponse(404, "")

    monkeypatch.setattr("app.services.crawler.httpx.Client", DummyClient)
    assert scraper._robots_allowed("https://example.org") is True


@pytest.mark.asyncio
async def test_fetch_html_and_playwright_helpers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scraper = ComplianceScraper()

    class AsyncResponse:
        text = "<html></html>"

        def raise_for_status(self) -> None:
            return None

    class DummyAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self) -> "DummyAsyncClient":
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def get(self, _url: str) -> AsyncResponse:
            return AsyncResponse()

    monkeypatch.setattr("app.services.crawler.httpx.AsyncClient", DummyAsyncClient)
    html = await scraper._fetch_html("https://example.org")
    assert html == "<html></html>"

    class DummyPage:
        async def goto(self, *_args, **_kwargs) -> None:
            return None

        async def content(self) -> str:
            return "<html><body>ok</body></html>"

    class DummyBrowser:
        async def new_page(self) -> DummyPage:
            return DummyPage()

        async def close(self) -> None:
            return None

    class DummyChromium:
        async def launch(self, **_kwargs) -> DummyBrowser:
            return DummyBrowser()

    class DummyPlaywright:
        chromium = DummyChromium()

    class DummyContextManager:
        async def __aenter__(self) -> DummyPlaywright:
            return DummyPlaywright()

        async def __aexit__(self, *args) -> None:
            return None

    monkeypatch.setattr(
        "app.services.crawler.async_playwright",
        lambda: DummyContextManager(),
    )
    rendered = await scraper._fetch_html_with_playwright("https://example.org")
    assert "ok" in rendered
