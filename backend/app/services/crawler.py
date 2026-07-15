import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

from app.core.errors import AppError

EMAIL_REGEX = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MISSION_KEYWORDS = ("mission", "about", "who we are", "our purpose")
LOCATION_KEYWORDS = ("location", "address", "headquarters")
CONTACT_KEYWORDS = ("contact", "email", "reach")


class ComplianceScraper:
    def _robots_allowed(self, target_url: str) -> bool:
        parsed = urlparse(target_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = RobotFileParser()

        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(robots_url)
            if response.status_code == 404:
                return True
            parser.parse(response.text.splitlines())
            return parser.can_fetch("*", target_url)
        except Exception:
            return True

    async def _fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    async def _fetch_html_with_playwright(self, url: str) -> str:
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=10_000, wait_until="networkidle")
                content = await page.content()
                await browser.close()
                return content
        except PlaywrightError as exc:
            raise AppError(f"Failed rendering page with Playwright: {exc}") from exc

    def _extract_text(self, soup: BeautifulSoup) -> str:
        for tag in soup(["script", "style", "noscript", "meta"]):
            tag.extract()
        return " ".join(segment.strip() for segment in soup.stripped_strings)

    def _extract_mission(self, soup: BeautifulSoup) -> str | None:
        for element in soup.find_all(["h1", "h2", "h3", "p"]):
            text = element.get_text(" ", strip=True)
            if any(keyword in text.lower() for keyword in MISSION_KEYWORDS):
                return text[:500]
        return None

    def _extract_location(self, soup: BeautifulSoup) -> str | None:
        for element in soup.find_all(["p", "li", "span", "div"]):
            text = element.get_text(" ", strip=True)
            lowered = text.lower()
            if any(keyword in lowered for keyword in LOCATION_KEYWORDS):
                return text[:255]
        return None

    def _extract_contact(self, soup: BeautifulSoup) -> tuple[str | None, str | None]:
        text = soup.get_text(" ", strip=True)
        matches = EMAIL_REGEX.findall(text)
        email = matches[0] if matches else None

        contact = None
        for link in soup.find_all("a"):
            href = (link.get("href") or "").strip()
            if href.startswith("mailto:") and email is None:
                email = href.removeprefix("mailto:").strip() or None
            label = link.get_text(" ", strip=True)
            if any(keyword in label.lower() for keyword in CONTACT_KEYWORDS):
                contact = label[:255]
                break

        return email, contact

    def _candidate_links(self, url: str, soup: BeautifulSoup) -> list[str]:
        parsed = urlparse(url)
        candidates: list[str] = []
        for anchor in soup.find_all("a", href=True):
            full_url = urljoin(url, anchor["href"])
            target = urlparse(full_url)
            if target.netloc != parsed.netloc:
                continue
            if any(
                word in full_url.lower() for word in ("about", "mission", "contact")
            ):
                candidates.append(full_url)
        return candidates[:3]

    async def extract_profile(self, url: str) -> dict[str, str | None]:
        if not self._robots_allowed(url):
            raise AppError(f"robots.txt disallows crawling for {url}")

        html: str
        try:
            html = await self._fetch_html(url)
        except Exception:
            html = await self._fetch_html_with_playwright(url)

        soup = BeautifulSoup(html, "html.parser")
        combined_soup = BeautifulSoup(html, "html.parser")

        for link in self._candidate_links(url, soup):
            if not self._robots_allowed(link):
                continue
            try:
                sub_html = await self._fetch_html(link)
            except Exception:
                continue
            sub_soup = BeautifulSoup(sub_html, "html.parser")
            for element in sub_soup.find_all(
                ["h1", "h2", "h3", "p", "li", "span", "div"]
            ):
                combined_soup.append(element)

        title = soup.title.get_text(strip=True) if soup.title else urlparse(url).netloc
        mission = self._extract_mission(combined_soup)
        location = self._extract_location(combined_soup)
        public_email, public_contact = self._extract_contact(combined_soup)

        description = self._extract_text(soup)

        return {
            "name": title[:255],
            "website": url,
            "mission": mission,
            "description": description[:600],
            "industry": None,
            "location": location,
            "public_email": public_email,
            "public_contact": public_contact,
            "notes": "Extracted from public website content.",
        }
