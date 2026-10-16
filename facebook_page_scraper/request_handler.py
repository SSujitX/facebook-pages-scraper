# facebook_page_scraper/request_handler.py

import curl_cffi
from selectolax.parser import HTMLParser
import json

GRAPHQL_URL = "https://www.facebook.com/api/graphql/"


def graphql_form(query: dict, variables: dict, lsd: str) -> dict:
    """Form body for one logged-out Relay request."""
    return {
        "av": "0",
        "__user": "0",
        "__a": "1",
        "lsd": lsd,
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": query["queryName"],
        "variables": json.dumps(variables),
        "doc_id": query["queryID"],
        "server_timestamps": "true",
    }


def graphql_lines(text: str) -> list[dict]:
    """A Relay response is one JSON object per line (first payload, streamed edges, deferred parts)."""
    text = text.removeprefix("for (;;);")
    return [json.loads(line) for line in text.splitlines() if line.strip()]

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

    def post_graphql(self, query: dict, variables: dict, lsd: str, referer: str) -> list[dict] | None:
        """Run a Relay query taken from the page HTML. Returns the response lines, or None on failure."""
        try:
            response = self.session.post(
                GRAPHQL_URL,
                headers={**self.headers, "x-fb-lsd": lsd, "origin": "https://www.facebook.com", "referer": referer},
                data=graphql_form(query, variables, lsd),
            )
            response.raise_for_status()
            return graphql_lines(response.text)
        except Exception as e:
            print(f"Error fetching posts [{referer}]: {e}")
            return None

    def close(self):
        session = self.session
        self.session = None
        if session is not None:
            session.close()

    def find_json(self, html_content: HTMLParser, key_to_find: str) -> dict | None:
        """Return the first JSON script containing key_to_find, or None."""
        return next(self.iter_json(html_content, key_to_find), None)

    def iter_json(self, html_content: HTMLParser, key_to_find: str):
        """Yield every JSON script containing key_to_find."""
        if html_content is None:
            return
        for script in html_content.css('script[type="application/json"]'):
            script_text = script.text(strip=True)
            if key_to_find not in script_text:
                continue
            try:
                yield json.loads(script_text)
            except json.JSONDecodeError:
                continue


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

    async def post_graphql(self, query: dict, variables: dict, lsd: str, referer: str) -> list[dict] | None:
        try:
            response = await self.session.post(
                GRAPHQL_URL,
                headers={**self.headers, "x-fb-lsd": lsd, "origin": "https://www.facebook.com", "referer": referer},
                data=graphql_form(query, variables, lsd),
            )
            response.raise_for_status()
            return graphql_lines(response.text)
        except Exception as e:
            print(f"Error fetching posts [{referer}]: {e}")
            return None

    async def close(self):
        session = self.session
        self.session = None
        if session is not None:
            await session.close()
