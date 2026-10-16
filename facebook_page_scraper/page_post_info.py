# facebook_page_scraper/page_post_info.py

import asyncio
import calendar
import time
from datetime import date, datetime, timezone
from typing import List, Optional, Dict

from .facebook_json import relay_results, walk
from .request_handler import RequestHandler
from .urls import normalize_url

FEED_QUERY = "ProfileCometTimelineFeedQuery"
# Facebook returns at most 40 posts per logged-out feed request.
PAGE_SIZE = 40
# Pause between feed requests so a long run does not trip rate limits.
PAGE_DELAY = 1.0


class PagePostInfo:
    def __init__(
        self,
        url: str,
        handler=None,
        proxy: str | None = None,
        max_posts: int | None = 1,
        since: datetime | date | int | float | str | None = None,
    ):
        """
        Initializes the PagePostInfo scraper with the given Facebook page URL or username.

        Args:
            url (str): The URL or username of the Facebook page to scrape posts from.
            proxy: Optional HTTP, HTTPS, or SOCKS proxy URL.
                Examples: ``http://user:pass@host:port``, ``socks5://host:port``.
            max_posts: Most posts to return. 1 reads only the page HTML. None means every post.
            since: Skip posts older than this date, datetime, ISO string, or unix time.
                A datetime without a timezone is UTC.
        """
        self.url = normalize_url(url)
        self._owns_handler = handler is None
        self.request_handler = handler if handler is not None else RequestHandler(proxy=proxy)
        self.posts: List[Dict[str, Optional[str]]] = []
        self.max_posts = max_posts
        self.since = _unix(since)

    def scrape(self) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Scrape the page's posts, newest first.

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
            pager = _Pager(self.extract_timeline_info(timeline_info_json), self.max_posts, self.since)
            request = _feed_request(self.request_handler, html_content) if not pager.done() else None
            while request and not pager.done():
                query, lsd = request
                lines = self.request_handler.post_graphql(query, pager.variables(query), lsd, self.url)
                if lines is None:
                    break
                pager.add(self.extract_graphql_posts(lines), self.url)
                if not pager.done():
                    time.sleep(PAGE_DELAY)
            self.posts = pager.result()
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
        pager = _Pager(self.extract_timeline_info(timeline_info_json), self.max_posts, self.since)
        request = _feed_request(self.request_handler, html_content) if not pager.done() else None
        while request and not pager.done():
            query, lsd = request
            lines = await self.request_handler.post_graphql(query, pager.variables(query), lsd, self.url)
            if lines is None:
                break
            pager.add(self.extract_graphql_posts(lines), self.url)
            if not pager.done():
                await asyncio.sleep(PAGE_DELAY)
        self.posts = pager.result()
        return self.posts

    def extract_timeline_info(self, json_data: dict) -> Optional[List[Dict[str, Optional[str]]]]:
        """Posts preloaded in the page HTML. Facebook preloads only the latest one."""
        timeline_info = []

        try:
            for result in relay_results(json_data):
                timeline = _dig(result, "data", "user", "timeline_list_feed_units") or {}
                edges = timeline.get("edges") if isinstance(timeline, dict) else None
                for story_node in edges or []:
                    if not isinstance(story_node, dict):
                        continue
                    node = story_node.get("node") or {}
                    if node:
                        timeline_info.append(_post(node))
            return timeline_info
        except (IndexError, KeyError, TypeError, ValueError, AttributeError) as e:
            print(f"Error extracting posts: {e}")
            return timeline_info

    def extract_graphql_posts(self, lines: list) -> List[Dict[str, Optional[str]]]:
        """Posts from a feed response: edges in the first line, then one streamed edge per line."""
        found = []
        for line in lines:
            data = line.get("data") if isinstance(line, dict) else None
            if not isinstance(data, dict):
                continue
            timeline = _dig(data, "user", "timeline_list_feed_units") or {}
            nodes = [(edge or {}).get("node") for edge in (timeline.get("edges") or [])]
            nodes.append(data.get("node"))
            for node in nodes:
                if isinstance(node, dict) and (node.get("post_id") or node.get("permalink_url")):
                    found.append(_post(node))
        return found

    @classmethod
    def PagePostInfo(
        cls,
        url: str,
        proxy: str | None = None,
        max_posts: int | None = 1,
        since: datetime | date | int | float | str | None = None,
    ) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Class method to directly get page posts information without needing to instantiate the class.

        Args:
            url (str): The URL or username of the Facebook page to scrape posts from.
            max_posts: Most posts to return. None means every post.
            since: Skip posts older than this.

        Returns:
            list: A list of dictionaries containing posts information, or None if extraction fails.
        """
        scraper = cls(url, proxy=proxy, max_posts=max_posts, since=since)
        return scraper.scrape()


class _Pager:
    """Walks the feed back in time with beforeTime, keeping posts in order and unique."""

    def __init__(self, posts: list, max_posts: int | None, since: int | None):
        self.max_posts = max_posts
        self.since = since
        self.posts: list = []
        self.seen: set = set()
        self.before: int | None = None
        self.finished = False
        self._keep(posts)

    def _keep(self, posts: list) -> int:
        added = 0
        for post in posts:
            created = post.get("creation_time")
            if isinstance(created, int):
                self.before = created if self.before is None else min(self.before, created)
            key = post.get("id") or post.get("url")
            if key in self.seen:
                continue
            self.seen.add(key)
            if self.since is not None and isinstance(created, int) and created < self.since:
                self.finished = True
                continue
            self.posts.append(post)
            added += 1
        return added

    def done(self) -> bool:
        if self.finished:
            return True
        return self.max_posts is not None and len(self.posts) >= self.max_posts

    def variables(self, query: dict) -> dict:
        return dict(query["variables"], count=PAGE_SIZE, beforeTime=self.before)

    def add(self, posts: list, url: str):
        if not self._keep(posts):
            self.finished = True
        oldest = time.strftime("%Y-%m-%d", time.gmtime(self.before)) if self.before else "?"
        print(f"[{url}] {len(self.posts)} posts, back to {oldest}")

    def result(self) -> list:
        return self.posts if self.max_posts is None else self.posts[: self.max_posts]


def _feed_request(handler, html_content):
    """The page's own timeline query and LSD token, both read from the HTML."""
    query = lsd = None
    for blob in handler.iter_json(html_content, FEED_QUERY):
        query = next(
            (
                item for item in walk(blob)
                if isinstance(item, dict)
                and item.get("queryName") == FEED_QUERY
                and item.get("queryID")
                and isinstance(item.get("variables"), dict)
            ),
            None,
        )
        if query:
            break
    for blob in handler.iter_json(html_content, '"LSD"'):
        lsd = next(
            (
                item[2]["token"] for item in walk(blob)
                if isinstance(item, list) and len(item) > 2 and item[0] == "LSD"
                and isinstance(item[2], dict) and item[2].get("token")
            ),
            None,
        )
        if lsd:
            break
    if not query or not lsd:
        print("Timeline query or LSD token not found in the HTML page. Returning the preloaded posts only.")
        return None
    return query, lsd


def _unix(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return int(value.timestamp())
    if isinstance(value, date):
        return calendar.timegm(value.timetuple())
    return int(value)


def _post(node: dict) -> Dict[str, Optional[str]]:
    return {
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
    }


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
        if not isinstance(attachment, dict):
            continue
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
