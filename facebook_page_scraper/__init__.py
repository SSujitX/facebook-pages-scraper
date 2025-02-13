# facebook_page_scraper/__init__.py

from .page_info import PageInfo
from .page_post_info import PagePostInfo
from typing import List, Optional, Dict
from .__version__ import __version__


class FacebookPageScraper:
    """
    A unified interface to access various Facebook page scraping features.
    """

    @staticmethod
    def PageInfo(url: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Fetches general page information.

        Args:
            url (str): The URL or username of the Facebook page to scrape.

        Returns:
            dict: A dictionary with general page information, or None if extraction fails.
        """
        return PageInfo.PageInfo(url)

    @staticmethod
    def PagePostInfo(url: str) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Fetches page posts information.

        Args:
            url (str): The URL or username of the Facebook page to scrape posts from.

        Returns:
            list: A list of dictionaries containing posts information, or None if extraction fails.
        """
        return PagePostInfo.PagePostInfo(url)


__all__ = ["FacebookPageScraper", "PageInfo", "PagePostInfo"]
