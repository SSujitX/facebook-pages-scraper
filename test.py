from facebook_page_scraper import FacebookPageScraper
from rich import print


def main():
    urls = [
        "/instagram",
        "https://www.facebook.com/facebook",
        "https://www.facebook.com/MadKingXGaming/",
        "https://www.facebook.com/LinkedIn",
    ]

    for url in urls:
        print(f">= Scraping URL/Username: {url}")
        page_info = FacebookPageScraper.PageInfo(url)
        print(page_info)


if __name__ == "__main__":
    main()
