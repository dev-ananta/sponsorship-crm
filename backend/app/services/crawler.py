import re
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class ComplianceScraper:
    @staticmethod
    def verify_robots_txt(target_url: str) -> bool:
        """Verifies if crawling the target URL is permitted by robots.txt."""
        parsed = urlparse(target_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        rp = RobotFileParser()
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(robots_url)
                if resp.status_code == 404:
                    return True
                rp.parse(resp.text.splitlines())
            return rp.can_fetch("*", target_url)
        except Exception:
            return True  # Permissive error boundary fallback

    async def extract_profile(self, url: str) -> dict:
        """Crawls accessible content and extracts public organization metadata."""
        if not self.verify_robots_txt(url):
            raise PermissionError(f"Scrape forbidden by target rules on: {url}")

        html_content = ""
        # Primary: Fast programmatic HTTP pull
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    html_content = response.text
        except Exception:
            pass

        # Secondary fallback: Render SPA pages using Playwright headless browser
        if not html_content:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, wait_until="networkidle", timeout=7000)
                    html_content = await page.content()
                    await browser.close()
            except Exception as e:
                return {"name": urlparse(url).netloc, "website": url, "notes": f"Scrape completed with connectivity failure: {e}"}

        # Structure Parser Engine
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script/style tag artifacts
        for element in soup(["script", "style", "meta"]):
            element.extract()
        
        visible_text = soup.get_text(separator=" ")
        
        # Regular expression filters for publicly listed emails
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', visible_text)
        public_email = emails[0] if emails else None
        
        # Strategic metadata lookups
        page_title = soup.title.string.strip() if soup.title else urlparse(url).netloc
        
        # Factual parsing boundaries (no hallucinated assumptions allowed)
        mission_statement = None
        for heading in soup.find_all(["h1", "h2", "h3", "p"]):
            text = heading.get_text()
            if "mission" in text.lower() or "who we are" in text.lower():
                mission_statement = text.strip()[:500]
                break

        return {
            "name": page_title,
            "website": url,
            "mission": mission_statement,
            "description": visible_text.strip()[:300],
            "public_email": public_email,
            "industry": "Discovered"
        }
