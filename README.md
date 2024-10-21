[![PyPI version](https://badge.fury.io/py/facebook-pages-scraper.svg)](https://badge.fury.io/py/facebook-pages-scraper)
[![Python Versions](https://img.shields.io/pypi/pyversions/facebook-pages-scraper.svg)](https://pypi.org/project/facebook-pages-scraper/)

# Facebook Page Scraper

**Facebook Page Scraper** is a Python package designed to extract comprehensive information from Facebook pages. Whether you're looking to gather general page details or delve into specific profile information, this tool simplifies the process, saving you time and effort. Easily integrate it into your projects to collect data such as page name, URL, profile picture, number of likes, followers, and more.

With Facebook Page Scraper, you can efficiently scrape Facebook page data in various formats. If you're looking for a **Facebook page scraper**, a **Facebook page info scraper in Python**, or an easy way to **scrape Facebook page info**, this tool has you covered. It's also ideal for developers who need to **extract Facebook page information** or **scrape Facebook data** using Python. You can even find it on **GitHub** and integrate it into your project seamlessly.

If you find this package useful, please support the project by giving it a star on [GitHub](https://github.com/SSujitX/facebook-page-scraper). Your support helps in maintaining and enhancing the project!

### Features:

- **Initial Release - Facebook Page Scraper v0.0.1**
- **Page Name & URL Extraction**: Easily extract the name and URL of the Facebook page.
- **Profile Picture Scraping**: Retrieve the profile picture associated with the page.
- **Likes & Followers Count**: Get the number of likes and followers for the page.
- **Category Information**: Scrape the page's category (e.g., App Page, Product/Service).
- **Email & Phone**: Extract associated email addresses and phone numbers (if available).
- **Website & Social Media Links**: Retrieve website links and social media profiles connected to the page.
- **Business Hours & Services**: Scrape business hours and services (where applicable).
- **Simple Integration**: Built with ease of use in mind, allowing quick integration into Python projects for Facebook page data automation.

This release lays the foundation for future updates and enhancements, providing developers with a reliable way to gather Facebook page data programmatically.

## Installation

- You can install this package using pip:

```sh
pip install facebook-pages-scraper
```

- You can upgrade this package using pip (upgrade to latest version):

```sh
pip install facebook-pages-scraper --upgrade
```

## Usage

### Scraping General Page Information

The following example demonstrates how to scrape general information from a Facebook page using the `FacebookPageScraper` class.

```python
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
        print(f">= Scraping URL/Username: {url}\n")

        page_info = FacebookPageScraper.PageInfo(url)
        print("Page Information:")
        print(page_info)
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()


# Output
    # >= Scraping URL/Username: /instagram
    # {
    #     'page_name': 'Instagram',
    #     'page_url': 'https://www.facebook.com/instagram',
    #     'profile_pic':
    # 'https://scontent.fdac22-2.fna.fbcdn.net/v/t39.30808-1/281523213_5154082218010914_1249949579548042028_n.jpg?stp=dst-jpg_s200x
    # 200&_nc_cat=1&ccb=1-7&_nc_sid=f4b9fd&_nc_ohc=xO9172fM8iwQ7kNvgGJTeKm&_nc_zt=24&_nc_ht=scontent.fdac22-2.fna&_nc_gid=AxLYcAimX
    # PGqMhaTor0fRo_&oh=00_AYDt0G7UAg72JlSXc_9zHpAJxTV282cZGHpJXePHDa8O5Q&oe=671B59A9',
    #     'page_likes': '61M likes',
    #     'page_followers': '68M followers',
    #     'page_category': 'Page · App Page',
    #     'page_address': None,
    #     'page_phone': None,
    #     'page_email': None,
    #     'page_website': 'instagram.com',
    #     'page_business_hours': None,
    #     'page_business_price': None,
    #     'page_rating': None,
    #     'page_services': None,
    #     'page_social_accounts': None
    # }
```

# Disclaimer

⚠️ Important Notice

Facebook's Terms of Service and Community Standards prohibit unauthorized scraping of their platform. This package is intended for educational purposes, and you should use it in compliance with Facebook's policies. Unauthorized scraping or accessing Facebook data without permission can result in legal consequences or a permanent ban from the platform.

By using Facebook Page Scraper, you acknowledge that:

You have the right and permission to access the data you are scraping.
You are solely responsible for how you use this package and for any consequences that may arise.
The developers of this tool are not liable for any misuse, and it is your responsibility to ensure compliance with Facebook's rules and regulations.
