import asyncio

from selectolax.parser import HTMLParser

from facebook_page_scraper import FacebookPageScraper
from facebook_page_scraper.page_info import PageInfo
from facebook_page_scraper.page_post_info import PagePostInfo
from facebook_page_scraper.request_handler import AsyncRequestHandler, RequestHandler
from facebook_page_scraper.urls import normalize_url


def test_normalize_url():
    assert normalize_url("bbcnews") == "https://www.facebook.com/bbcnews"
    assert (
        normalize_url("https://web.facebook.com/pizzaburgbd?_rdc=1&_rdr")
        == "https://www.facebook.com/pizzaburgbd"
    )
    assert normalize_url("https://m.facebook.com/Meta") == "https://www.facebook.com/Meta"


def test_find_json_and_missing_key():
    handler = RequestHandler()
    try:
        html = HTMLParser(
            '<script type="application/json">{"username_for_profile": 1}</script>'
        )
        assert handler.find_json(html, "username_for_profile")["username_for_profile"] == 1
        assert handler.find_json(html, "missing") is None
        assert handler.find_json(None, "username_for_profile") is None
    finally:
        handler.close()
        handler.close()


def test_fetch_failure_returns_none(monkeypatch):
    handler = RequestHandler()

    def boom(*_args, **_kwargs):
        raise RuntimeError("down")

    monkeypatch.setattr(handler.session, "get", boom)
    assert handler.fetch_html("https://www.facebook.com/bbcnews") is None
    handler.close()


def test_sync_failure_is_none_not_exit(monkeypatch):
    monkeypatch.setattr(RequestHandler, "fetch_html", lambda self, url: None)
    assert PageInfo.PageInfo("bbcnews") is None
    assert PagePostInfo.PagePostInfo("bbcnews") is None
    assert FacebookPageScraper.PageInfo(["bbcnews", "NASA"]) == [None, None]
    assert FacebookPageScraper.PagePostInfo(["bbcnews"]) == [None]


def test_async_failure_is_none_not_exit(monkeypatch):
    async def no_html(self, url):
        return None

    monkeypatch.setattr(AsyncRequestHandler, "fetch_html", no_html)
    assert asyncio.run(FacebookPageScraper.PageInfoAsync("bbcnews")) is None
    assert asyncio.run(FacebookPageScraper.PageInfoAsync(["bbcnews", "NASA"])) == [None, None]
    assert asyncio.run(FacebookPageScraper.PagePostInfoAsync("bbcnews")) is None
