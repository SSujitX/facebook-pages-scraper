# facebook_page_scraper/__init__.py

import asyncio
from datetime import date, datetime
from importlib.metadata import version
from pathlib import Path

from .page_info import PageInfo
from .page_post_info import PagePostInfo
from .request_handler import AsyncRequestHandler
from .storage import save_json, save_result

__version__ = version("facebook-pages-scraper")


async def _many_async(scraper_cls, urls: str | list[str], concurrency: int, proxy: str | None, **options):
    async def one(url: str):
        async with semaphore:
            handler = AsyncRequestHandler(proxy=proxy)
            try:
                return await scraper_cls(url, handler, **options).scrape_async()
            except Exception as exc:
                print(f"Error scraping [{url}]: {exc}")
                return None
            finally:
                await handler.close()

    semaphore = asyncio.Semaphore(concurrency)
    if isinstance(urls, str):
        return await one(urls)
    return list(await asyncio.gather(*[one(url) for url in urls]))


class FacebookPageScraper:
    """
    A unified interface to access various Facebook page scraping features.

    A string returns one result. A list returns one result per page, in order.
    proxy is an optional HTTP, HTTPS, or SOCKS URL, for example
    ``http://user:pass@host:port`` or ``socks5://host:port``.
    save_to is an optional file path. The result is also written there as JSON.
    """

    @staticmethod
    def PageInfo(
        url: str | list[str], proxy: str | None = None, save_to: str | Path | None = None
    ):
        """
        Fetches general page information.

        Args:
            url: One page URL or username, or a list of them.
            proxy: Optional HTTP, HTTPS, or SOCKS proxy URL.
            save_to: Optional JSON file path for the result.

        Returns:
            One dict, or a list of dicts when url is a list. A failed page is None.
        """
        if isinstance(url, str):
            result = PageInfo.PageInfo(url, proxy=proxy)
        else:
            result = [PageInfo.PageInfo(item, proxy=proxy) for item in url]
        return save_result(result, save_to)

    @staticmethod
    async def PageInfoAsync(
        url: str | list[str],
        concurrency: int = 4,
        proxy: str | None = None,
        save_to: str | Path | None = None,
    ):
        """Async PageInfo. A list fetches up to concurrency pages at once."""
        return save_result(await _many_async(PageInfo, url, concurrency, proxy), save_to)

    @staticmethod
    def PagePostInfo(
        url: str | list[str],
        proxy: str | None = None,
        save_to: str | Path | None = None,
        max_posts: int | None = 1,
        since: datetime | date | int | float | str | None = None,
    ):
        """
        Fetches page posts, newest first.

        Args:
            url: One page URL or username, or a list of them.
            proxy: Optional HTTP, HTTPS, or SOCKS proxy URL.
            save_to: Optional JSON file path for the result.
            max_posts: Most posts per page. 1 reads only the page HTML. None means every post.
            since: Skip posts older than this date, datetime, ISO string, or unix time (UTC).

        Returns:
            One list of posts, or a list of those lists when url is a list.
        """
        options = {"proxy": proxy, "max_posts": max_posts, "since": since}
        if isinstance(url, str):
            result = PagePostInfo.PagePostInfo(url, **options)
        else:
            result = [PagePostInfo.PagePostInfo(item, **options) for item in url]
        return save_result(result, save_to)

    @staticmethod
    async def PagePostInfoAsync(
        url: str | list[str],
        concurrency: int = 4,
        proxy: str | None = None,
        save_to: str | Path | None = None,
        max_posts: int | None = 1,
        since: datetime | date | int | float | str | None = None,
    ):
        """Async PagePostInfo. A list fetches up to concurrency pages at once."""
        result = await _many_async(
            PagePostInfo, url, concurrency, proxy, max_posts=max_posts, since=since
        )
        return save_result(result, save_to)


__all__ = ["FacebookPageScraper", "PageInfo", "PagePostInfo", "save_json"]
