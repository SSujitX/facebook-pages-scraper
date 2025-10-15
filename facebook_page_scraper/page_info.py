# facebook_page_scraper/page_info.py


from typing import Optional, Dict
from .request_handler import RequestHandler, HTMLParser, re


class PageInfo:
    def __init__(self, url: str):
        """
        Initializes the PageInfo scraper with the given Facebook page URL or username.

        Args:
            url (str): The URL or username of the Facebook page to scrape.
        """
        self.url = self.normalize_url(url)
        self.request_handler = RequestHandler()
        self.general_info: Dict[str, Optional[str]] = {}
        self.profile_info: Dict[str, Optional[str]] = {}

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

    def scrape(self) -> Optional[Dict[str, Optional[str]]]:
        """
        Performs the scraping process to retrieve general and profile page information.

        Returns:
            dict: A combined dictionary with general and profile page information, or None if extraction fails.
        """
        html_content = self.request_handler.fetch_html(self.url)

        # Parse general information
        general_info_json = self.request_handler.parse_json_from_html(
            html_content, "username_for_profile"
        )
        self.general_info = self.extract_general_info(general_info_json)

        # Parse profile information
        profile_info_json = self.request_handler.parse_json_from_html(
            html_content, "profile_tile_items"
        )
        self.profile_info = self.extract_profile_info(profile_info_json)
        
        self.meta_html_info = self.extract_html_data(html_content)

        # Combine both into one dictionary
        if self.general_info and self.profile_info:
            combined_info = {**self.general_info, **self.meta_html_info, **self.profile_info}
            return combined_info
        elif self.general_info:
            return self.general_info
        elif self.profile_info:
            return self.profile_info
        else:
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
            "page_id" : None,
            "is_business_page" : None
        }

        try:
            requires = json_data.get("require", [])
            if not requires:
                raise ValueError("Missing 'require' key in JSON data.")
            requires = requires[0][3][0].get("__bbox", {}).get("require", [])

            for require in requires:
                if "RelayPrefetchedStreamCache" in require:
                    result = require[3][1].get("__bbox", {}).get("result", {})
                    user = (
                        result.get("data", {})
                        .get("user", {})
                        .get("profile_header_renderer", {})
                        .get("user", {})
                    )

                    general_info["page_name"] = user.get("name")
                    general_info["page_url"] = user.get("url")
                    
                    general_info["page_id"] = user.get("delegate_page", {}).get("id")
                    
                    general_info["is_business_page"] = user.get("delegate_page", {}).get("is_business_page_active")

                    general_info["profile_pic"] = (
                        user.get("profilePicLarge", {}).get("uri")
                        or user.get("profilePicMedium", {}).get("uri")
                        or user.get("profilePicSmall", {}).get("uri")
                    )
                    
                    general_info["cover_photo"] = user.get("cover_photo", {}).get("photo", {}).get("image",{}).get("uri")

                    profile_social_contents = user.get(
                        "profile_social_context", {}
                    ).get("content", [])
                    for content in profile_social_contents:
                        uri = content.get("uri", "")
                        text = content.get("text", {}).get("text")
                        if "friends_likes" in uri and not general_info["page_likes"]:
                            general_info["page_likes"] = text
                        elif "followers" in uri and not general_info["page_followers"]:
                            general_info["page_followers"] = text
                        if (
                            general_info["page_likes"]
                            and general_info["page_followers"]
                        ):
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
        }

        profile_info = {value: None for value in matching_types.values()}

        try:
            requires = json_data.get("require", [])
            if not requires:
                raise ValueError("Missing 'require' key in JSON data.")
            requires = requires[0][3][0].get("__bbox", {}).get("require", [])

            for require in requires:
                if "RelayPrefetchedStreamCache" in require:
                    result = require[3][1].get("__bbox", {}).get("result", {})
                    profile_tile_sections = (
                        result.get("data", {})
                        .get("profile_tile_sections", {})
                        .get("edges", [])
                    )

                    for section in profile_tile_sections:
                        nodes = (
                            section.get("node", {})
                            .get("profile_tile_views", {})
                            .get("nodes", [])
                        )
                        for node in nodes:
                            view_style_renderer = node.get("view_style_renderer")
                            if not view_style_renderer:
                                continue
                            profile_tile_items = (
                                view_style_renderer.get("view", {})
                                .get("profile_tile_items", {})
                                .get("nodes", [])
                            )
                            for item in profile_tile_items:
                                timeline_context_item = item.get("node", {}).get(
                                    "timeline_context_item", {}
                                )
                                item_type = timeline_context_item.get(
                                    "timeline_context_list_item_type"
                                )
                                if item_type in matching_types:
                                    text = (
                                        timeline_context_item.get("renderer", {})
                                        .get("context_item", {})
                                        .get("title", {})
                                        .get("text")
                                    )
                                    if text:
                                        key = matching_types[item_type]
                                        profile_info[key] = text
            return profile_info
        except (IndexError, KeyError, TypeError, ValueError) as e:
            print(f"Error extracting profile information: {e}")
            return profile_info

    def extract_html_data(self, html_content: HTMLParser) -> Dict[str, Optional[str]]:
        """Extracts the JSON data from the HTML content. 
        
        Args:
            html_content (str): The raw HTML content of the page.
        
        Returns:
            dict: A dictionary with the extracted JSON data.
        """
        meta_data = {
                    "page_likes_count": None,
                    "page_talking_count": None,
                    "page_were_here_count": None,
                }
        
        try:

            meta_description = html_content.css_first("meta[name=description]").attrs.get("content") if html_content.css_first("meta[name=description]") else None
            
            if not meta_description:
                return meta_data
            
            like_pattern = r"(?P<likes>[\d,]+)\s+likes"
            like_match = re.search(like_pattern, meta_description)
            likes = like_match.group("likes") if like_match else None

            talking_pattern = r"(?P<talking>[\d,]+)\s+talking about this"
            talking_match = re.search(talking_pattern, meta_description)
            talking = talking_match.group("talking") if talking_match else None

            were_pattern = r"(?P<were>[\d,]+)\s+were here"
            were_match = re.search(were_pattern, meta_description)
            were = were_match.group("were") if were_match else None

            meta_data["page_likes_count"] = likes
            meta_data["page_talking_count"] = talking
            meta_data["page_were_here_count"] = were
            
            return meta_data
        
        except Exception as e:
            print(
                f"Unexpected error in (extract_html_data) func: {e}")
            return meta_data

    @classmethod
    def PageInfo(cls, url: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Class method to directly get page information without needing to instantiate the class.

        Args:
            url (str): The URL or username of the Facebook page to scrape.

        Returns:
            dict: A combined dictionary with general and profile page information, or None if extraction fails.
        """
        scraper = cls(url)
        return scraper.scrape()
