import asyncio

from facebook_page_scraper import FacebookPageScraper
from rich.pretty import pprint


async def main():
    urls = [
        "https://web.facebook.com/bbcnews",
        "https://web.facebook.com/NASA",
        "https://web.facebook.com/Meta",
        "https://web.facebook.com/Google",
        "https://web.facebook.com/Microsoft",
        "https://web.facebook.com/Netflix",
        "https://web.facebook.com/nike",
        "https://web.facebook.com/adidas",
        "https://web.facebook.com/Samsung",
        "https://web.facebook.com/pizzaburgbd",
    ]

    pprint(f">= Scraping {len(urls)} pages")

    pages = await FacebookPageScraper.PageInfoAsync(urls, concurrency=4)
    for url, page_info in zip(urls, pages):
        pprint(f">= Scraping URL/Username: {url}")
        pprint("Page Information:")
        pprint(page_info)
        pprint("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
