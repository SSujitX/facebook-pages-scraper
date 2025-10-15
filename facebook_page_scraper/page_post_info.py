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
        html_content = self.request_handler.fetch_html(self.url)

        # Parse timeline information
        timeline_info_json = self.request_handler.parse_json_from_html(
            html_content, "timeline_list_feed_units"
        )
        self.posts = self.extract_timeline_info(timeline_info_json)

        return self.posts

    def extract_timeline_info(self, json_data: dict) -> Optional[List[Dict[str, Optional[str]]]]:
        timeline_info = []
        
        try:
            requires = json_data.get("require", [])
            if not requires:
                raise ValueError("Missing 'require' key in JSON data.")
            requires = requires[0][3][0].get("__bbox", {}).get("require", [])

            for require in requires:
                if "RelayPrefetchedStreamCache" in require:
                    result = require[3][1].get("__bbox", {}).get("result", {})
                    timeline = result.get("data", {}).get("user", {}).get("timeline_list_feed_units", {})

                    for story_node in timeline.get("edges", []):
                        story ={
                            "id" :None,
                            "creation_time":None,
                            "text":None,
                            "medias":[]
                        }
                        story["id"] = story_node.get("node", {}).get("id")
                        story["creation_time"] = story_node.get("node", {}).get("comet_sections", {}).get("timestamp", {}).get("story", {}).get("creation_time")
                        story["text"] = story_node.get("node", {}).get("comet_sections", {}).get("content", {}).get("story", {}).get("comet_sections", {}).get("message", {}).get("story", {}).get("message", {}).get("text")

                        for attachment in story_node.get("node", {}).get("attachments",[]):
                            for media_node in attachment.get("styles", {}).get("attachment", {}).get("all_subattachments", {}).get("nodes",[]):
                                media = {
                                    "__typename" :None,
                                    "height":None,
                                    "width":None,
                                    "uri":None
                                }
                                media["__typename"] = media_node.get("media", {}).get("__typename")
                                media["height"] = media_node.get("media", {}).get("viewer_image", {}).get("height")
                                media["width"] = media_node.get("media", {}).get("viewer_image", {}).get("width")
                                media["uri"] = media_node.get("media", {}).get("viewer_image", {}).get("uri")
                                media["accessibility_caption"] = media_node.get("media", {}).get("accessibility_caption")

                                story["medias"].append(media)

                        timeline_info.append(story)                        

            return timeline_info

        except (IndexError, KeyError, TypeError, ValueError) as e:
            print(f"Error extracting profile information: {e}")
            return timeline_info

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
