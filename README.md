<p align="center">
  <a href="https://badge.fury.io/py/facebook-pages-scraper"><img src="https://badge.fury.io/py/facebook-pages-scraper.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/facebook-pages-scraper/"><img src="https://img.shields.io/badge/python-%3E%3D3.11-blue" alt="Python >=3.11"></a>
  <a href="https://pepy.tech/project/facebook-pages-scraper"><img src="https://static.pepy.tech/badge/facebook-pages-scraper" alt="Downloads"></a>
  <a href="https://pepy.tech/project/facebook-pages-scraper"><img src="https://static.pepy.tech/badge/facebook-pages-scraper/week" alt="Downloads this week"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/SSujitX/facebook-pages-scraper/master/assets/banner.jpg" alt="Facebook Pages Scraper">
</p>

# Facebook Pages Scraper

Facebook Pages Scraper reads public Facebook page info and posts without a browser or an API key. If you find it useful, please support the package by hitting the star on GitHub. Your support helps keep the project going.

Use **facebook-pages-scraper** for a page name, intro, about text, contact fields, and posts. A string returns one result. A list returns one result per page. Works with `pip install facebook-pages-scraper` or `uv add facebook-pages-scraper` on Python 3.11+.

<details>
<summary><strong>Looking for a sponsor</strong></summary>

<a href="mailto:ssujitxx@gmail.com">ssujitxx@gmail.com</a>
</details>

## Demo

![Scrape a Facebook page](https://raw.githubusercontent.com/SSujitX/facebook-pages-scraper/master/assets/facebook-pages-scraper.gif)

## How it works

The package fetches the public page HTML with a Chrome-like client, then reads the JSON Facebook embeds in that document.

Page info comes from the profile header and intro cards. Address, the About paragraph, page id, and creation date come from the About tab. The page HTML preloads only the latest post. For more, the scraper re-sends the timeline query found in that HTML, 40 posts per request, stepping back in time until it reaches `max_posts`, `since`, or the page's first post.

Accepted input:

- `bbcnews`
- `https://www.facebook.com/bbcnews`
- `https://web.facebook.com/bbcnews`
- `https://m.facebook.com/bbcnews`

`pizzaburgbd` is a public page that fills the About fields: intro, about text, address, phone, email, website, hours, services, Instagram, owner, page id, and creation date. Use it when you want a test run to show a full result. Page likes and the Monday–Sunday hours grid are still absent, because Facebook does not put them in this HTML.

A string returns one dict (or one list of posts). A list returns one result per page, in order. A failed page is `None`.

`page_social_accounts` is a map of network to link, for example `{"Instagram": "https://www.instagram.com/meta"}`. Page likes are often missing from the public HTML. `page_business_hours` is the open/closed line Facebook sends with the page, not the Monday–Sunday grid.

## Installation

```sh
uv add facebook-pages-scraper
```

```sh
pip install facebook-pages-scraper
```

```sh
pip install facebook-pages-scraper --upgrade
```

This repo uses [uv](https://docs.astral.sh/uv/):

```sh
uv sync --group dev
```

## Parameters

| Parameter | Default | What it is |
|---|---|---|
| `url` | required | One page URL or username, or a list of them. |
| `proxy` | `None` | Optional HTTP/HTTPS/SOCKS5 proxy if this IP is rate-limited. |
| `concurrency` | `4` | **Async list only.** Max pages fetched at once. |
| `max_posts` | `1` | **Posts only.** Most posts per page, newest first. `1` reads just the page HTML. `None` means every post. |
| `since` | `None` | **Posts only.** Skip posts older than this `date`, `datetime`, ISO string (`"2026-01-01"`), or unix time. UTC. |
| `save_to` | `None` | Optional file path. The result is also written there as UTF-8 JSON. Folders are created. A failed page (`None`) is not written. |

`proxy` stays `None` unless you need one. Examples:

```text
http://user:pass@host:port
https://host:port
socks5://user:pass@host:port
```

## Usage

### Sync — `PageInfo`

```python
from facebook_page_scraper import FacebookPageScraper


def main():
    # Optional. Examples:
    #   proxy = "http://user:pass@host:port"
    #   proxy = "https://host:port"
    #   proxy = "socks5://user:pass@host:port"
    proxy = None

    url = "https://web.facebook.com/pizzaburgbd"

    try:
        page = FacebookPageScraper.PageInfo(url, proxy=proxy)
        if page:
            print(page)
        else:
            print("Error: no page data")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
```

### Async — `PageInfoAsync`

```python
import asyncio

from facebook_page_scraper import FacebookPageScraper


def main():
    # Optional. Examples:
    #   proxy = "http://user:pass@host:port"
    #   proxy = "https://host:port"
    #   proxy = "socks5://user:pass@host:port"
    proxy = None

    url = "https://web.facebook.com/pizzaburgbd"

    try:
        page = asyncio.run(FacebookPageScraper.PageInfoAsync(url, proxy=proxy))
        if page:
            print(page)
        else:
            print("Error: no page data")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
```

### Async batch

Pass a list. Up to `concurrency` pages run at once.

```python
import asyncio

from facebook_page_scraper import FacebookPageScraper


def main():
    # Optional. Examples:
    #   proxy = "http://user:pass@host:port"
    #   proxy = "https://host:port"
    #   proxy = "socks5://user:pass@host:port"
    proxy = None

    urls = [
        "https://web.facebook.com/pizzaburgbd",
        "https://web.facebook.com/NASA",
        "https://web.facebook.com/Meta",
    ]

    try:
        pages = asyncio.run(
            FacebookPageScraper.PageInfoAsync(urls, concurrency=4, proxy=proxy)
        )
        for page in pages:
            if page:
                print("Page:", page["page_name"])
            else:
                print("Error: no page data")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
```

`FacebookPageScraper.PageInfo(urls)` also accepts a list (sync, one page after another). For many pages, async batch is the better call.

`PagePostInfo` and `PagePostInfoAsync` take the same `url`, `proxy`, `concurrency`, and `save_to` arguments, plus `max_posts` and `since`. A string returns one list of posts. A list of pages returns a list of those lists.

### Posts

```python
from facebook_page_scraper import FacebookPageScraper

# Latest post only (one request)
FacebookPageScraper.PagePostInfo("lgucabanatuan")

# Latest 100 posts
FacebookPageScraper.PagePostInfo("lgucabanatuan", max_posts=100)

# Every post since a date, saved to a file
FacebookPageScraper.PagePostInfo(
    "lgucabanatuan", max_posts=None, since="2026-07-01",
    save_to="output/lgucabanatuan/posts.json",
)
```

Each request returns up to 40 posts and takes about 4 MB, with a 1 second pause between requests. A page with years of daily posts can mean hundreds of requests, so set `since` or `max_posts` unless you need the full history. If a request fails partway, you get the posts collected so far. A shared post with no caption of its own has `text: null`.

### Save to a file

Pass `save_to` to any call. The result is still returned.

```python
from facebook_page_scraper import FacebookPageScraper

FacebookPageScraper.PageInfo("lgucabanatuan", save_to="output/lgucabanatuan/page_info.json")
FacebookPageScraper.PagePostInfo("lgucabanatuan", save_to="output/lgucabanatuan/posts.json")
```

A list of pages saves one JSON array in input order, with `null` for a failed page. Image links in the saved file are signed by Facebook and expire after a few days.

## Disclaimer

Facebook's Terms of Service and Community Standards prohibit unauthorized scraping of their platform. This package is intended for educational purposes, and you should use it in compliance with Facebook's policies. Unauthorized scraping or accessing Facebook data without permission can result in legal consequences or a permanent ban from the platform.

By using Facebook Pages Scraper, you acknowledge that you have the right to access the data you are scraping, and that you are solely responsible for how you use this package. The developers of this tool are not liable for any misuse.

## Star History

[![Star History Chart](https://api.star-history.com/chart?repos=SSujitX/facebook-pages-scraper&type=date&legend=top-left&sealed_token=B4YLot1P-IIlvJ98r7p7hM9O1e8oUA3XPtevpc011R4Zzwv_FSyAxK5y596wURJ3SLg7vYApWqwucWdS3jtkmLfWHvWM9Wa0rzyILK4VEnES5SuyQIXrRM-yji4pEkjvIkZTgExlk8LZH5UFXxLfvWJMjPS30bWvuFFGhsD5Coi4KPS2CHrL2qhTx9LC)](https://www.star-history.com/?repos=SSujitX%2Ffacebook-pages-scraper&type=date&legend=top-left)

![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2FSSujitX%2Ffacebook-pages-scraper&countColor=%23263759&labelStyle=upper)
