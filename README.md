[![PyPI version](https://badge.fury.io/py/facebook-pages-scraper.svg)](https://badge.fury.io/py/facebook-pages-scraper)
[![Python Versions](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13-blue)](https://pypi.org/project/facebook-pages-scraper/)
[![Downloads](https://static.pepy.tech/badge/facebook-pages-scraper)](https://pepy.tech/project/facebook-pages-scraper)
[![Downloads](https://static.pepy.tech/badge/facebook-pages-scraper/month)](https://pepy.tech/project/facebook-pages-scraper)
[![Downloads](https://static.pepy.tech/badge/facebook-pages-scraper/week)](https://pepy.tech/project/facebook-pages-scraper)

# Facebook Page Scraper

**Facebook Page Scraper** is a Python client package/library that helps you grab Facebook page data without the hassle. Need basic stuff like page names and profile pics? Or maybe you're after business details, follower counts, and engagement stats? This Python package does it all with minimal code. Perfect for developers looking to **scrape Facebook page info** without wasting time. This **Facebook page info scraper in Python** cuts out hours of manual work and gives you clean, ready-to-use results. It handles all kinds of pages, pulls **Facebook page information** without login headaches, and fits right into your existing projects - whether you're building a dashboard, running analysis, or keeping tabs on competitors. Found on **GitHub** and PyPI, our **Facebook page scraper** is straightforward enough for newcomers but packed with features that make **Facebook data extraction** a breeze for seasoned coders too.

If you find this package useful, please support the project by giving it a star on [GitHub](https://github.com/SSujitX/facebook-pages-scraper). Your support helps in maintaining and enhancing the project!

## Update

- **Version 0.0.4**:
  - **Fixed**: Improved error handling for missing user data in page_info.py.
  - **Fixed**: Added proper null checks for delegate_page and profile_social_context.
  - **Improved**: Enhanced robustness against Facebook API structure changes.

### Features:

- **Page Name & URL Extraction**: Easily extract the name and URL of the Facebook page
- **Profile Picture Access**: Get high-quality profile picture URLs
- **Basic Metrics**: Extract likes, followers, talking count, and check-ins
- **Page Identity**: Get page ID and business page status
- **Detailed Statistics**: Access precise counts for likes, engagements, and visitor metrics
- **Business Information**:
  - Category and classification
  - Physical address
  - Contact details (phone and email)
  - Website URL
  - Operating hours
  - Price range indicators
  - Available services
- **Rating Information**: Access page ratings when available
- **Social Media Integration**: Retrieve connected social media accounts
- **Simple Integration**: Easy to integrate into any Python project

## Installation

- You can install this package using pip:

```sh
pip install facebook-pages-scraper
```

- You can upgrade this package using pip (upgrade to the latest version):

```sh
pip install facebook-pages-scraper --upgrade
```

- Using uv:

```sh
uv add facebook-pages-scraper -U
```

## Usage

### Scraping General Page Information

The following example demonstrates how to scrape general information from a Facebook page using the `FacebookPageScraper` class.

```python
from facebook_page_scraper import FacebookPageScraper
from rich.pretty import pprint

def main():
    url = "https://www.facebook.com/pizzaburgbd"

    pprint(f">= Scraping URL/Username: {url}")

    page_info = FacebookPageScraper.PageInfo(url)
    pprint("Page Information:")
    pprint(page_info)
    pprint("=" * 80)

if __name__ == "__main__":
    main()
```

### Using a for loop to scrape multiple URLs

```python
from facebook_page_scraper import FacebookPageScraper
from rich.pretty import pprint
import time

def main():
    urls = [
        "/instagram",
        "https://www.facebook.com/facebook",
        "https://www.facebook.com/MadKingXGaming/",
        "https://www.facebook.com/LinkedIn",
        "https://www.facebook.com/pizzaburgbd"
    ]

    for url in urls:
        pprint(f">= Scraping URL/Username: {url}")

        page_info = FacebookPageScraper.PageInfo(url)
        pprint("Page Information:")
        pprint(page_info)
        pprint("=" * 80)
        time.sleep(2)


if __name__ == "__main__":
    main()
```

### Possible output

```sh
{
│   'page_name': 'PizzaBurg',
│   'page_url': 'https://www.facebook.com/pizzaburgbd',
│   'profile_pic': 'https://scontent.fdac22-2.fna.fbcdn.net/v/t39.30808-1/461120046_932810008890332_7328117254384510587_n.jpg?stp=cp6_dst-jpg_s200x200_tt6&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_nc_ohc=lMP1pZatZ90Q7kNvgEBx2nl&_nc_oc=AdhqTswSuZ36AUvf955zvso4FUy1qUvAUsTwzwik8lijO-NNmFLmxAhqyDFtGI-rllw&_nc_zt=24&_nc_ht=scontent.fdac22-2.fna&_nc_gid=ADEDzW-U1qvrumGbDCHzumc&oh=00_AYAo2NWsmCr_qa0IZc3Nwj_7K_-DVrgkuidp1PGhvXcFjg&oe=67B3145F',
│   'page_likes': '412K likes',
│   'page_followers': '614K followers',
│   'page_id': '1156899667774877',
│   'is_business_page': True,
│   'page_likes_count': '412,723',
│   'page_talking_count': '26,076',
│   'page_were_here_count': '64,824',
│   'page_category': 'Page · Fast food restaurant',
│   'page_address': 'Avenue Road Section:2 , Block: A, Avenue:1 , House: 12/1, Dhaka 1216, Dhaka, Bangladesh',
│   'page_phone': '01404-461200',
│   'page_email': 'pizzaburgofficial@gmail.com',
│   'page_website': 'pizzaburg.com',
│   'page_business_hours': 'Closed now',
│   'page_business_price': 'Price range · £',
│   'page_rating': None,
│   'page_services': 'Dine in · In-store collection',
│   'page_social_accounts': None
}
```

# Disclaimer

⚠️ Important Notice

Facebook's Terms of Service and Community Standards prohibit unauthorized scraping of their platform. This package is intended for educational purposes, and you should use it in compliance with Facebook's policies. Unauthorized scraping or accessing Facebook data without permission can result in legal consequences or a permanent ban from the platform.

By using Facebook Page Scraper, you acknowledge that:

You have the right and permission to access the data you are scraping.
You are solely responsible for how you use this package and for any consequences that may arise.
The developers of this tool are not liable for any misuse, and it is your responsibility to ensure compliance with Facebook's rules and regulations.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=SSujitX/facebook-pages-scraper&type=date&legend=top-left)](https://www.star-history.com/#SSujitX/facebook-pages-scraper&type=date&legend=top-left)

![](https://api.visitorbadge.io/api/VisitorHit?user=SSujitX&facebook-pages-scraper&countColor=%237B1E7A)
