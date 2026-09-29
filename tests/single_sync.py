from facebook_page_scraper import FacebookPageScraper
from rich.pretty import pprint


def main():
    url = "https://web.facebook.com/bbcnews"

    pprint(f">= Scraping URL/Username: {url}")

    page_info = FacebookPageScraper.PageInfo(url)
    pprint("Page Information:")
    pprint(page_info)
    pprint("=" * 80)


if __name__ == "__main__":
    main()
