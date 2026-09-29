import asyncio

from selectolax.parser import HTMLParser

from facebook_page_scraper import FacebookPageScraper
from facebook_page_scraper.page_info import PageInfo
from facebook_page_scraper.page_post_info import PagePostInfo
from facebook_page_scraper.request_handler import AsyncRequestHandler, RequestHandler
from facebook_page_scraper.urls import normalize_url


def test_normalize_url():
    assert normalize_url("bbcnews") == "https://www.facebook.com/bbcnews"
    assert (
        normalize_url("https://web.facebook.com/pizzaburgbd?_rdc=1&_rdr")
        == "https://www.facebook.com/pizzaburgbd"
    )
    assert normalize_url("https://m.facebook.com/Meta") == "https://www.facebook.com/Meta"


def test_find_json_and_missing_key():
    handler = RequestHandler()
    try:
        html = HTMLParser(
            '<script type="application/json">{"username_for_profile": 1}</script>'
        )
        assert handler.find_json(html, "username_for_profile")["username_for_profile"] == 1
        assert handler.find_json(html, "missing") is None
        assert handler.find_json(None, "username_for_profile") is None
    finally:
        handler.close()
        handler.close()


def test_fetch_failure_returns_none(monkeypatch):
    handler = RequestHandler()

    def boom(*_args, **_kwargs):
        raise RuntimeError("down")

    monkeypatch.setattr(handler.session, "get", boom)
    assert handler.fetch_html("https://www.facebook.com/bbcnews") is None
    handler.close()


def test_sync_failure_is_none_not_exit(monkeypatch):
    monkeypatch.setattr(RequestHandler, "fetch_html", lambda self, url: None)
    assert PageInfo.PageInfo("bbcnews") is None
    assert PagePostInfo.PagePostInfo("bbcnews") is None
    assert FacebookPageScraper.PageInfo(["bbcnews", "NASA"]) == [None, None]
    assert FacebookPageScraper.PagePostInfo(["bbcnews"]) == [None]


def test_async_failure_is_none_not_exit(monkeypatch):
    async def no_html(self, url):
        return None

    monkeypatch.setattr(AsyncRequestHandler, "fetch_html", no_html)
    assert asyncio.run(FacebookPageScraper.PageInfoAsync("bbcnews")) is None
    assert asyncio.run(FacebookPageScraper.PageInfoAsync(["bbcnews", "NASA"])) == [None, None]
    assert asyncio.run(FacebookPageScraper.PagePostInfoAsync("bbcnews")) is None


def _relay(result):
    return {
        "require": [[
            0, 0, 0,
            [{"__bbox": {"require": [[
                "RelayPrefetchedStreamCache", 0, 0,
                [0, {"__bbox": {"result": result}}],
            ]]}}],
        ]],
    }


def _header(cover_photo, user=None):
    if user is None:
        user = {
            "name": "Example",
            "url": "https://www.facebook.com/example",
            "cover_photo": cover_photo,
        }
    return _relay({"data": {"user": {"profile_header_renderer": {"user": user}}}})


def _card(item_type, title, subtitle=None):
    context = {"title": title}
    if subtitle is not None:
        context["subtitle"] = subtitle
    return {
        "node": {
            "timeline_context_item": {
                "timeline_context_list_item_type": item_type,
                "renderer": {"context_item": context},
            }
        }
    }


def _profile(items):
    return _relay({
        "data": {
            "profile_tile_sections": {
                "edges": [
                    None,
                    {"node": None},
                    {
                        "node": {
                            "profile_tile_views": {
                                "nodes": [
                                    {"view_style_renderer": None},
                                    {
                                        "view_style_renderer": {
                                            "view": {"profile_tile_items": {"nodes": items}},
                                        }
                                    },
                                ]
                            }
                        }
                    },
                ]
            }
        }
    })


def test_null_cover_photo_is_none():
    scraper = PageInfo("example", handler=object())
    missing = scraper.extract_general_info(_header(None))
    assert missing["page_name"] == "Example"
    assert missing["cover_photo"] is None
    present = scraper.extract_general_info(
        _header({"photo": {"image": {"uri": "https://example.com/cover.jpg"}}})
    )
    assert present["cover_photo"] == "https://example.com/cover.jpg"


def test_null_profile_pic_and_followers_text():
    scraper = PageInfo("example", handler=object())
    user = {
        "name": "Example",
        "profilePicLarge": None,
        "profilePicMedium": None,
        "profilePicSmall": None,
        "cover_photo": None,
        "profile_social_context": {"content": [{"uri": "/followers", "text": None}]},
    }
    info = scraper.extract_general_info(_header(None, user=user))
    assert info["page_name"] == "Example"
    assert info["profile_pic"] is None
    assert info["page_followers"] is None
    assert info["cover_photo"] is None


def test_profile_pic_falls_through_null_sizes():
    scraper = PageInfo("example", handler=object())
    user = {
        "name": "Example",
        "profilePicLarge": None,
        "profilePicMedium": {"uri": "https://example.com/pic.jpg"},
        "delegate_page": None,
    }
    info = scraper.extract_general_info(_header(None, user=user))
    assert info["profile_pic"] == "https://example.com/pic.jpg"
    assert info["page_id"] is None


def test_null_header_objects_keep_the_page():
    scraper = PageInfo("example", handler=object())
    info = scraper.extract_general_info(_relay({"data": None}))
    assert info["page_name"] is None
    assert info["cover_photo"] is None
    info = scraper.extract_general_info(_relay({"data": {"user": None}}))
    assert info["page_name"] is None


def test_null_intro_title_skips_that_card_only():
    scraper = PageInfo("example", handler=object())
    items = [
        None,
        {"node": None},
        _card("INTRO_CARD_ADDRESS", None),
        _card("INTRO_CARD_PROFILE_PHONE", {"text": "01404-461200"}),
        _card(
            "INTRO_CARD_OTHER_ACCOUNT",
            {
                "text": "Instagram",
                "ranges": [{"entity": {"external_url": "https://www.instagram.com/pizzaburgofficial"}}],
            },
        ),
        _card("INTRO_CARD_CONFIRMED_OWNER_LABEL", {"text": "PIZZA BURG"}, {"text": "is responsible for this Page"}),
    ]
    info = scraper.extract_profile_info(_profile(items))
    assert info["page_address"] is None
    assert info["page_phone"] == "01404-461200"
    assert info["page_social_accounts"] == {
        "Instagram": "https://www.instagram.com/pizzaburgofficial",
    }
    assert info["page_owner"] == "PIZZA BURG is responsible for this Page"


def test_null_profile_sections_return_empty_cards():
    scraper = PageInfo("example", handler=object())
    info = scraper.extract_profile_info(_relay({"data": None}))
    assert info["page_phone"] is None
    assert info["page_social_accounts"] == {}


def test_null_post_nodes_keep_a_real_post():
    posts = PagePostInfo("example", handler=object())
    payload = _relay({
        "data": {
            "user": {
                "timeline_list_feed_units": {
                    "edges": [
                        None,
                        {"node": None},
                        {
                            "node": {
                                "post_id": "1",
                                "permalink_url": "https://www.facebook.com/example/posts/1",
                                "creation_time": 10,
                                "comet_sections": None,
                                "attachments": [None, {"styles": None}],
                            }
                        },
                    ]
                }
            }
        }
    })
    found = posts.extract_timeline_info(payload)
    assert len(found) == 1
    assert found[0]["id"] == "1"
    assert found[0]["url"] == "https://www.facebook.com/example/posts/1"
    assert found[0]["text"] is None
    assert found[0]["medias"] == []


def test_null_timeline_is_an_empty_list():
    posts = PagePostInfo("example", handler=object())
    found = posts.extract_timeline_info(_relay({"data": {"user": {"timeline_list_feed_units": None}}}))
    assert found == []


def test_null_relay_bbox_does_not_crash():
    scraper = PageInfo("example", handler=object())
    broken = {"require": [[0, 0, 0, [{"__bbox": None}]]]}
    assert scraper.extract_general_info(broken)["page_name"] is None
    assert scraper.extract_profile_info(broken)["page_social_accounts"] == {}
    assert PagePostInfo("example", handler=object()).extract_timeline_info(broken) == []
