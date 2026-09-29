# facebook_page_scraper/__init__.py

import asyncio
from importlib.metadata import version

from .page_info import PageInfo
from .page_post_info import PagePostInfo
from .request_handler import AsyncRequestHandler

__version__ = version("facebook-pages-scraper")


async def _many_async(scraper_cls, urls: str | list[str], concurrency: int, proxy: str | None):
    async def one(url: str):
        async with semaphore:
            handler = AsyncRequestHandler(proxy=proxy)
            try:
                return await scraper_cls(url, handler).scrape_async()
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
    """

    @staticmethod
    def PageInfo(url: str | list[str], proxy: str | None = None):
        """
        Fetches general page information.

        Args:
            url: One page URL or username, or a list of them.
            proxy: Optional HTTP, HTTPS, or SOCKS proxy URL.

        Returns:
            One dict, or a list of dicts when url is a list. A failed page is None.
        """
        if isinstance(url, str):
            return PageInfo.PageInfo(url, proxy=proxy)
        return [PageInfo.PageInfo(item, proxy=proxy) for item in url]

    @staticmethod
    async def PageInfoAsync(url: str | list[str], concurrency: int = 4, proxy: str | None = None):
        """Async PageInfo. A list fetches up to concurrency pages at once."""
        return await _many_async(PageInfo, url, concurrency, proxy)

    @staticmethod
    def PagePostInfo(url: str | list[str], proxy: str | None = None):
        """
        Fetches page posts information.

        Args:
            url: One page URL or username, or a list of them.
            proxy: Optional HTTP, HTTPS, or SOCKS proxy URL.

        Returns:
            One list of posts, or a list of those lists when url is a list.
        """
        if isinstance(url, str):
            return PagePostInfo.PagePostInfo(url, proxy=proxy)
        return [PagePostInfo.PagePostInfo(item, proxy=proxy) for item in url]

    @staticmethod
    async def PagePostInfoAsync(
        url: str | list[str], concurrency: int = 4, proxy: str | None = None
    ):
        """Async PagePostInfo. A list fetches up to concurrency pages at once."""
        return await _many_async(PagePostInfo, url, concurrency, proxy)


__all__ = ["FacebookPageScraper", "PageInfo", "PagePostInfo"]
