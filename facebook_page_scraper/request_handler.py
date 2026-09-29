# facebook_page_scraper/request_handler.py

import curl_cffi
from selectolax.parser import HTMLParser
import json

class RequestHandler:
    def __init__(self, proxy: str | None = None):
        # One Chrome session: TLS, headers, and cookies stay consistent.
        # A custom or rotating user-agent disagrees with that fingerprint.
        self.session = curl_cffi.Session(impersonate="chrome", proxy=proxy)
        self.headers = {"accept-language": "en-US,en;q=0.9"}

    def fetch_html(self, url: str):
        """Fetch url. Returns parsed HTML, or None when the request fails."""
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return HTMLParser(response.text)
        except Exception as e:
            print(f"Error fetching the page [{url}]: {e}")
            return None

    def close(self):
        session = self.session
        self.session = None
        if session is not None:
            session.close()

    def find_json(self, html_content: HTMLParser, key_to_find: str) -> dict | None:
        """Return the first JSON script containing key_to_find, or None."""
        if html_content is None:
            return None
        for script in html_content.css('script[type="application/json"]'):
            script_text = script.text(strip=True)
            if key_to_find not in script_text:
                continue
            try:
                return json.loads(script_text)
            except json.JSONDecodeError:
                continue
        return None


class AsyncRequestHandler(RequestHandler):
    """Same Chrome impersonation as RequestHandler, on an async session."""

    def __init__(self, proxy: str | None = None):
        self.session = curl_cffi.AsyncSession(impersonate="chrome", proxy=proxy)
        self.headers = {"accept-language": "en-US,en;q=0.9"}

    async def fetch_html(self, url: str):
        try:
            response = await self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return HTMLParser(response.text)
        except Exception as e:
            print(f"Error fetching the page [{url}]: {e}")
            return None

    async def close(self):
        session = self.session
        self.session = None
        if session is not None:
            await session.close()
