[![PyPI version](https://badge.fury.io/py/facebook-pages-scraper.svg)](https://badge.fury.io/py/facebook-pages-scraper)
[![Python Versions](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13-blue)](https://pypi.org/project/facebook-pages-scraper/)
[![Downloads](https://static.pepy.tech/badge/facebook-pages-scraper)](https://pepy.tech/project/facebook-pages-scraper)
[![Downloads](https://static.pepy.tech/badge/facebook-pages-scraper/month)](https://pepy.tech/project/facebook-pages-scraper)
[![Downloads](https://static.pepy.tech/badge/facebook-pages-scraper/week)](https://pepy.tech/project/facebook-pages-scraper)

# Facebook Page Scraper

**Facebook Page Scraper** is a Python package designed to extract comprehensive information from Facebook pages. Whether you're looking to gather general page details or delve into specific profile information, this tool simplifies the process, saving you time and effort. Easily integrate it into your projects to collect data such as page name, URL, profile picture, number of likes, followers, and more.

With Facebook Page Scraper, you can efficiently scrape Facebook page data in various formats. If you're looking for a **Facebook page scraper**, a **Facebook page info scraper in Python**, or an easy way to **scrape Facebook page info**, this tool has you covered. It's also ideal for developers who need to **extract Facebook page information** or **scrape Facebook data** using Python. You can even find it on **GitHub** and integrate it into your project seamlessly.

If you find this package useful, please support the project by giving it a star on [GitHub](https://github.com/SSujitX/facebook-pages-scraper). Your support helps in maintaining and enhancing the project!

## Update

- **Version 0.0.3**:
  - **Updated**: Added extraction of additional data such as (cover photo).
  - **Improved**: Enhanced error handling.
  - **Added**: Initialization of PagePostInfo.
  - **New Contributor**: @olivier-saugeon made their first contribution.

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
