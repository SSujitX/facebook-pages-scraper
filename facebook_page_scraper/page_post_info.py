# facebook_page_scraper/page_post_info.py

from typing import List, Optional, Dict
from .request_handler import RequestHandler


class PagePostInfo:
    def __init__(self, url: str):
        """
        Initializes the PagePostInfo scraper with the given Facebook page URL or username.

        Args:
            url (str): The URL or username of the Facebook page to scrape posts from.
        """
        self.url = self.normalize_url(url)
        self.request_handler = RequestHandler()
        self.posts: List[Dict[str, Optional[str]]] = []

    @staticmethod
    def normalize_url(input_url: str) -> str:
        """
        Ensures that the given URL or username is formatted as a full Facebook page URL.

        Args:
            input_url (str): The URL or username.

        Returns:
            str: The normalized full URL.
        """
        base_url = "https://www.facebook.com/"
        if not input_url.startswith(base_url):
            # If it's a username or partial URL, append it to the base Facebook URL
            if input_url.startswith("/"):
                input_url = input_url[1:]  # Remove leading slash
            return base_url + input_url
        return input_url

    def scrape(self) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Placeholder method for scraping posts information.

        Returns:
            list: A list of dictionaries containing post information, or None if extraction fails.
        """
        # Optionally, raise an exception to clearly inform users
        raise NotImplementedError(
            "PagePostInfo is a future feature and is not yet implemented."
        )

    @classmethod
    def PagePostInfo(cls, url: str) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Class method to directly get page posts information without needing to instantiate the class.

        Args:
            url (str): The URL or username of the Facebook page to scrape posts from.

        Returns:
            list: A list of dictionaries containing posts information, or None if extraction fails.
        """
        scraper = cls(url)
        return scraper.scrape()
