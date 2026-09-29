# facebook_page_scraper/page_post_info.py

from typing import List, Optional, Dict

from .facebook_json import relay_results
from .request_handler import RequestHandler
from .urls import normalize_url


class PagePostInfo:
    def __init__(self, url: str, handler=None, proxy: str | None = None):
        """
        Initializes the PagePostInfo scraper with the given Facebook page URL or username.

        Args:
            url (str): The URL or username of the Facebook page to scrape posts from.
            proxy: Optional HTTP, HTTPS, or SOCKS proxy URL.
                Examples: ``http://user:pass@host:port``, ``socks5://host:port``.
        """
        self.url = normalize_url(url)
        self._owns_handler = handler is None
        self.request_handler = handler if handler is not None else RequestHandler(proxy=proxy)
        self.posts: List[Dict[str, Optional[str]]] = []

    def scrape(self) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Placeholder method for scraping posts information.

        Returns:
            list: A list of dictionaries containing post information, or None if extraction fails.
        """
        try:
            html_content = self.request_handler.fetch_html(self.url)
            if html_content is None:
                return None
            timeline_info_json = self.request_handler.find_json(
                html_content, "timeline_list_feed_units"
            )
            if not timeline_info_json:
                print("No valid data found for key 'timeline_list_feed_units' in the HTML page.")
                return None
            self.posts = self.extract_timeline_info(timeline_info_json)
            return self.posts
        finally:
            if self._owns_handler:
                self.request_handler.close()

    async def scrape_async(self) -> Optional[List[Dict[str, Optional[str]]]]:
        html_content = await self.request_handler.fetch_html(self.url)
        if html_content is None:
            return None
        timeline_info_json = self.request_handler.find_json(html_content, "timeline_list_feed_units")
        if not timeline_info_json:
            print("No valid data found for key 'timeline_list_feed_units' in the HTML page.")
            return None
        self.posts = self.extract_timeline_info(timeline_info_json)
        return self.posts

    def extract_timeline_info(self, json_data: dict) -> Optional[List[Dict[str, Optional[str]]]]:
        """The first page HTML contains only the latest timeline post."""
        timeline_info = []

        try:
            for result in relay_results(json_data):
                timeline = result.get("data", {}).get("user", {}).get("timeline_list_feed_units", {})
                for story_node in timeline.get("edges", []):
                    node = story_node.get("node") or {}
                    if not node:
                        continue
                    timeline_info.append({
                        "id": node.get("post_id") or node.get("id"),
                        "url": node.get("permalink_url"),
                        "creation_time": node.get("creation_time"),
                        "text": _dig(
                            node,
                            "comet_sections", "content", "story", "comet_sections",
                            "message", "story", "message", "text",
                        ),
                        "reaction_count": _count(node, "reaction_count"),
                        "comment_count": _count(node, "comments", "total_count"),
                        "share_count": _count(node, "share_count"),
                        "medias": _medias(node.get("attachments") or []),
                    })
            return timeline_info
        except (IndexError, KeyError, TypeError, ValueError, AttributeError) as e:
            print(f"Error extracting posts: {e}")
            return timeline_info

    @classmethod
    def PagePostInfo(cls, url: str, proxy: str | None = None) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Class method to directly get page posts information without needing to instantiate the class.

        Args:
            url (str): The URL or username of the Facebook page to scrape posts from.

        Returns:
            list: A list of dictionaries containing posts information, or None if extraction fails.
        """
        scraper = cls(url, proxy=proxy)
        return scraper.scrape()


def _dig(obj, *keys):
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _count(obj, field: str, count_key: str = "count"):
    if isinstance(obj, dict):
        value = obj.get(field)
        if isinstance(value, dict) and isinstance(value.get(count_key), int):
            return value[count_key]
        for child in obj.values():
            found = _count(child, field, count_key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for child in obj:
            found = _count(child, field, count_key)
            if found is not None:
                return found
    return None


def _medias(attachments: list) -> list:
    found = []
    seen = set()
    for attachment in attachments:
        styles = (attachment.get("styles") or {}).get("attachment") or {}
        candidates = [styles.get("media"), attachment.get("media")]
        for sub in (styles.get("all_subattachments") or {}).get("nodes") or []:
            candidates.append((sub or {}).get("media"))
        for media in candidates:
            item = _media(media)
            if not item or item["uri"] in seen:
                continue
            seen.add(item["uri"])
            found.append(item)
    return found


def _media(media: dict) -> Optional[dict]:
    if not isinstance(media, dict):
        return None
    image = media.get("photo_image") or media.get("viewer_image") or media.get("image") or {}
    if not isinstance(image, dict):
        image = {}
    uri = image.get("uri") or media.get("playable_url") or media.get("browser_native_sd_url")
    if not uri:
        return None
    return {
        "__typename": media.get("__typename"),
        "height": image.get("height"),
        "width": image.get("width"),
        "uri": uri,
        "accessibility_caption": media.get("accessibility_caption"),
    }
