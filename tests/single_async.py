import asyncio

from facebook_page_scraper import FacebookPageScraper
from rich.pretty import pprint


async def main():
    url = "https://web.facebook.com/ananya.bagchi.469701"

    pprint(f">= Scraping URL/Username: {url}")

    page_info = await FacebookPageScraper.PageInfoAsync(url)
    pprint("Page Information:")
    pprint(page_info)
    pprint("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
