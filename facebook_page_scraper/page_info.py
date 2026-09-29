# facebook_page_scraper/page_info.py

import asyncio
import re
from typing import Optional, Dict

from selectolax.parser import HTMLParser

from .about_pages import (
    about_address,
    about_address_async,
    about_text,
    about_text_async,
    transparency,
    transparency_async,
)
from .facebook_json import relay_results, text_at
from .request_handler import RequestHandler
from .urls import normalize_url


def _dict(value):
    return value if isinstance(value, dict) else {}


class PageInfo:
    def __init__(self, url: str, handler=None, proxy: str | None = None):
        """
        Initializes the PageInfo scraper with the given Facebook page URL or username.

        Args:
            url (str): The URL or username of the Facebook page to scrape.
            proxy: Optional HTTP, HTTPS, or SOCKS proxy URL.
                Examples: ``http://user:pass@host:port``, ``socks5://host:port``.
        """
        self.url = normalize_url(url)
        self._owns_handler = handler is None
        self.request_handler = handler if handler is not None else RequestHandler(proxy=proxy)
        self.general_info: Dict[str, Optional[str]] = {}
        self.profile_info: Dict[str, Optional[str]] = {}

    @staticmethod
    def normalize_url(input_url: str) -> str:
        """Ensures that the given URL or username is a full Facebook page URL."""
        return normalize_url(input_url)

    def scrape(self) -> Optional[Dict[str, Optional[str]]]:
        """
        Performs the scraping process to retrieve general and profile page information.

        Returns:
            dict: A combined dictionary with general and profile page information, or None if extraction fails.
        """
        try:
            return self._scrape()
        finally:
            if self._owns_handler:
                self.request_handler.close()

    def _scrape(self) -> Optional[Dict[str, Optional[str]]]:
        html_content = self.request_handler.fetch_html(self.url)
        if html_content is None:
            return None
        general_info_json = self.request_handler.find_json(html_content, "username_for_profile")
        profile_info_json = self.request_handler.find_json(html_content, "profile_tile_items")
        if not general_info_json or not profile_info_json:
            print("No valid data found for page info in the HTML page.")
            return None

        self.general_info = self.extract_general_info(general_info_json)
        self.general_info["page_intro"] = text_at(
            self.request_handler.find_json(html_content, "best_description"),
            "best_description",
        )
        self.general_info["page_about"] = about_text(self.request_handler, self.url)
        page_transparency = transparency(self.request_handler, self.url)
        if page_transparency.get("page_id"):
            self.general_info["page_id"] = page_transparency["page_id"]
        self.general_info["page_creation_date"] = page_transparency.get("page_creation_date")

        self.profile_info = self.extract_profile_info(profile_info_json)
        if not self.profile_info.get("page_address"):
            self.profile_info["page_address"] = about_address(self.request_handler, self.url)

        self.meta_html_info = self.extract_html_data(html_content)

        if self.general_info and self.profile_info:
            return {**self.general_info, **self.meta_html_info, **self.profile_info}
        if self.general_info:
            return self.general_info
        if self.profile_info:
            return self.profile_info
        return None

    async def scrape_async(self) -> Optional[Dict[str, Optional[str]]]:
        """Async scrape. About requests run together after the main page is parsed."""
        html_content = await self.request_handler.fetch_html(self.url)
        if html_content is None:
            return None
        general_info_json = self.request_handler.find_json(html_content, "username_for_profile")
        profile_info_json = self.request_handler.find_json(html_content, "profile_tile_items")
        if not general_info_json or not profile_info_json:
            print("No valid data found for page info in the HTML page.")
            return None

        self.general_info = self.extract_general_info(general_info_json)
        self.general_info["page_intro"] = text_at(
            self.request_handler.find_json(html_content, "best_description"),
            "best_description",
        )
        self.profile_info = self.extract_profile_info(profile_info_json)
        self.meta_html_info = self.extract_html_data(html_content)

        async def _no_address():
            return None

        address_task = (
            about_address_async(self.request_handler, self.url)
            if not self.profile_info.get("page_address")
            else _no_address()
        )
        page_about, page_transparency, address = await asyncio.gather(
            about_text_async(self.request_handler, self.url),
            transparency_async(self.request_handler, self.url),
            address_task,
        )
        self.general_info["page_about"] = page_about
        if page_transparency.get("page_id"):
            self.general_info["page_id"] = page_transparency["page_id"]
        self.general_info["page_creation_date"] = page_transparency.get("page_creation_date")
        if address:
            self.profile_info["page_address"] = address

        if self.general_info and self.profile_info:
            return {**self.general_info, **self.meta_html_info, **self.profile_info}
        return None

    def extract_general_info(self, json_data: dict) -> Dict[str, Optional[str]]:
        """
        Extracts general page information (name, URL, profile picture, likes, followers).

        Args:
            json_data (dict): The parsed JSON data.

        Returns:
            dict: A dictionary with general page information.
        """
        general_info = {
            "page_name": None,
            "page_url": None,
            "profile_pic": None,
            "cover_photo": None,
            "page_likes": None,
            "page_followers": None,
            "page_id": None,
            "page_creation_date": None,
            "is_business_page": None,
            "page_intro": None,
            "page_about": None,
        }

        try:
            for result in relay_results(json_data):
                user = _dict(
                    _dict(_dict(_dict(result.get("data")).get("user")).get("profile_header_renderer")).get("user")
                )

                general_info["page_name"] = user.get("name")
                general_info["page_url"] = user.get("url")

                delegate_page = user.get("delegate_page")
                if isinstance(delegate_page, dict):
                    general_info["page_id"] = delegate_page.get("id")
                    general_info["is_business_page"] = delegate_page.get(
                        "is_business_page_active"
                    )

                general_info["profile_pic"] = (
                    _dict(user.get("profilePicLarge")).get("uri")
                    or _dict(user.get("profilePicMedium")).get("uri")
                    or _dict(user.get("profilePicSmall")).get("uri")
                )

                cover_photo = _dict(user.get("cover_photo"))
                photo = _dict(cover_photo.get("photo"))
                image = _dict(photo.get("image"))
                general_info["cover_photo"] = image.get("uri")
                profile_social_context = user.get("profile_social_context")
                contents = profile_social_context.get("content") if isinstance(profile_social_context, dict) else None
                for content in contents or []:
                    if not isinstance(content, dict):
                        continue
                    uri = content.get("uri") or ""
                    text = _dict(content.get("text")).get("text")
                    if "friends_likes" in uri and not general_info["page_likes"]:
                        general_info["page_likes"] = text
                    elif "followers" in uri and not general_info["page_followers"]:
                        general_info["page_followers"] = text
                    if general_info["page_likes"] and general_info["page_followers"]:
                        break
            return general_info
        except (IndexError, KeyError, TypeError, ValueError) as e:
            print(f"Error extracting general page information: {e}")
            return general_info

    def extract_profile_info(self, json_data: dict) -> Dict[str, Optional[str]]:
        """
        Extracts detailed profile information from the parsed JSON data.

        Args:
            json_data (dict): The parsed JSON data.

        Returns:
            dict: A dictionary with detailed profile information.
        """
        matching_types = {
            "INTRO_CARD_INFLUENCER_CATEGORY": "page_category",
            "INTRO_CARD_ADDRESS": "page_address",
            "INTRO_CARD_PROFILE_PHONE": "page_phone",
            "INTRO_CARD_PROFILE_EMAIL": "page_email",
            "INTRO_CARD_WEBSITE": "page_website",
            "INTRO_CARD_BUSINESS_HOURS": "page_business_hours",
            "INTRO_CARD_BUSINESS_PRICE": "page_business_price",
            "INTRO_CARD_RATING": "page_rating",
            "INTRO_CARD_BUSINESS_SERVICES": "page_services",
            "INTRO_CARD_OTHER_ACCOUNT": "page_social_accounts",
            "INTRO_CARD_CONFIRMED_OWNER_LABEL": "page_owner",
        }

        profile_info = {value: None for value in matching_types.values()}
        profile_info["page_social_accounts"] = {}

        try:
            for result in relay_results(json_data):
                sections = _dict(_dict(result.get("data")).get("profile_tile_sections")).get("edges") or []
                if not isinstance(sections, list):
                    continue
                for section in sections:
                    if not isinstance(section, dict):
                        continue
                    nodes = _dict(_dict(section.get("node")).get("profile_tile_views")).get("nodes") or []
                    if not isinstance(nodes, list):
                        continue
                    for node in nodes:
                        if not isinstance(node, dict):
                            continue
                        view_style_renderer = node.get("view_style_renderer")
                        if not isinstance(view_style_renderer, dict):
                            continue
                        items = _dict(_dict(view_style_renderer.get("view")).get("profile_tile_items")).get("nodes") or []
                        if not isinstance(items, list):
                            continue
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                            timeline_context_item = _dict(_dict(item.get("node")).get("timeline_context_item"))
                            item_type = timeline_context_item.get(
                                "timeline_context_list_item_type"
                            )
                            if item_type not in matching_types:
                                continue
                            renderer = timeline_context_item.get("renderer") or {}
                            context_item = renderer.get("context_item") or {}
                            title = context_item.get("title") or {}
                            text = title.get("text") if isinstance(title, dict) else None
                            if not text:
                                continue
                            key = matching_types[item_type]
                            if item_type == "INTRO_CARD_OTHER_ACCOUNT":
                                url = self._social_url(title) or text
                                network = self._social_network(url) or "Other"
                                profile_info["page_social_accounts"][network] = url
                            elif item_type == "INTRO_CARD_CONFIRMED_OWNER_LABEL":
                                subtitle = context_item.get("subtitle") or {}
                                sub = subtitle.get("text") if isinstance(subtitle, dict) else None
                                profile_info[key] = f"{text} {sub}".strip() if sub else text
                            else:
                                profile_info[key] = text
            return profile_info
        except (IndexError, KeyError, TypeError, ValueError, AttributeError) as e:
            print(f"Error extracting profile information: {e}")
            return profile_info

    @staticmethod
    def _social_url(title: dict) -> Optional[str]:
        ranges = title.get("ranges") or []
        if not ranges or not isinstance(ranges[0], dict):
            return None
        entity = ranges[0].get("entity") or {}
        return entity.get("external_url")

    @staticmethod
    def _social_network(url: Optional[str]) -> Optional[str]:
        if not url or "://" not in url:
            return None
        host = url.split("/")[2].lower()
        if host.startswith("www."):
            host = host[4:]
        return {
            "instagram.com": "Instagram",
            "tiktok.com": "TikTok",
            "youtube.com": "YouTube",
            "youtu.be": "YouTube",
            "x.com": "X",
            "twitter.com": "X",
            "linkedin.com": "LinkedIn",
            "threads.net": "Threads",
        }.get(host, host)

    def extract_html_data(self, html_content: HTMLParser) -> Dict[str, Optional[str]]:
        """Extracts like, talking, and were-here counts from the meta description."""
        meta_data = {
            "page_likes_count": None,
            "page_talking_count": None,
            "page_were_here_count": None,
        }

        try:
            meta = html_content.css_first("meta[name=description]")
            meta_description = meta.attrs.get("content") if meta else None
            if not meta_description:
                return meta_data

            like_match = re.search(r"(?P<likes>[\d,]+)\s+likes", meta_description)
            talking_match = re.search(r"(?P<talking>[\d,]+)\s+talking about this", meta_description)
            were_match = re.search(r"(?P<were>[\d,]+)\s+were here", meta_description)

            meta_data["page_likes_count"] = like_match.group("likes") if like_match else None
            meta_data["page_talking_count"] = talking_match.group("talking") if talking_match else None
            meta_data["page_were_here_count"] = were_match.group("were") if were_match else None
            return meta_data
        except Exception as e:
            print(f"Unexpected error in (extract_html_data) func: {e}")
            return meta_data

    @classmethod
    def PageInfo(cls, url: str, proxy: str | None = None) -> Optional[Dict[str, Optional[str]]]:
        """
        Class method to directly get page information without needing to instantiate the class.

        Args:
            url (str): The URL or username of the Facebook page to scrape.
            proxy: Optional HTTP, HTTPS, or SOCKS proxy URL.

        Returns:
            dict: A combined dictionary with general and profile page information, or None if extraction fails.
        """
        return cls(url, proxy=proxy).scrape()
