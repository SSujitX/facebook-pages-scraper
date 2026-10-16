import asyncio
import json

from selectolax.parser import HTMLParser

from facebook_page_scraper import FacebookPageScraper
from facebook_page_scraper.page_info import PageInfo
from facebook_page_scraper import page_post_info
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


def test_save_to_writes_utf8_json(monkeypatch, tmp_path):
    page = {"page_name": "Lungsod ng Cabanatuan", "page_social_accounts": {}}
    monkeypatch.setattr(PageInfo, "PageInfo", classmethod(lambda cls, url, proxy=None: page))
    path = tmp_path / "out" / "page.json"
    assert FacebookPageScraper.PageInfo("example", save_to=path) == page
    assert json.loads(path.read_text(encoding="utf-8")) == page

    posts = [{"id": "1", "text": "Magandang umaga 🌞"}]
    monkeypatch.setattr(PagePostInfo, "PagePostInfo", classmethod(lambda cls, url, **_: posts))
    path = tmp_path / "posts.json"
    FacebookPageScraper.PagePostInfo(["a", "b"], save_to=str(path))
    assert "🌞" in path.read_text(encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8")) == [posts, posts]


def test_save_to_skips_a_failed_page(monkeypatch, tmp_path):
    monkeypatch.setattr(RequestHandler, "fetch_html", lambda self, url: None)
    path = tmp_path / "page.json"
    assert FacebookPageScraper.PageInfo("bbcnews", save_to=path) is None
    assert not path.exists()

    async def no_html(self, url):
        return None

    monkeypatch.setattr(AsyncRequestHandler, "fetch_html", no_html)
    path = tmp_path / "batch.json"
    assert asyncio.run(FacebookPageScraper.PageInfoAsync(["a", "b"], save_to=path)) == [None, None]
    assert json.loads(path.read_text(encoding="utf-8")) == [None, None]


def _story(post_id, created):
    return {"post_id": post_id, "permalink_url": f"https://www.facebook.com/example/posts/{post_id}", "creation_time": created}


def _feed_html(posts):
    preload = {
        "queryName": "ProfileCometTimelineFeedQuery",
        "queryID": "123",
        "variables": {"count": 1, "userID": "42"},
    }
    timeline = _relay({
        "data": {"user": {"timeline_list_feed_units": {"edges": [{"node": p} for p in posts]}}}
    })
    return HTMLParser(
        f'<script type="application/json">{json.dumps(timeline)}</script>'
        f'<script type="application/json">{json.dumps({"x": [{"expectedPreloaders": [preload]}]})}</script>'
        f'<script type="application/json">{json.dumps({"define": [["LSD", [], {"token": "tok"}, 1]]})}</script>'
    )


def _feed_lines(posts):
    """First line holds one edge, the rest stream in one per line, like the real response."""
    lines = [{"data": {"user": {"timeline_list_feed_units": {"edges": [{"node": p} for p in posts[:1]]}}}}]
    lines += [{"label": "stream", "data": {"node": p}} for p in posts[1:]]
    return lines


def _fake_feed(monkeypatch, timeline):
    """timeline is newest first. The fake server honors beforeTime and count like Facebook."""
    calls = []
    monkeypatch.setattr(page_post_info, "PAGE_DELAY", 0)
    monkeypatch.setattr(RequestHandler, "fetch_html", lambda self, url: _feed_html(timeline[:1]))

    def post_graphql(self, query, variables, lsd, referer):
        calls.append(variables)
        assert (query["queryID"], lsd, variables["userID"]) == ("123", "tok", "42")
        before = variables["beforeTime"]
        older = [p for p in timeline if before is None or p["creation_time"] <= before]
        return _feed_lines(older[: variables["count"]])

    monkeypatch.setattr(RequestHandler, "post_graphql", post_graphql)
    return calls


def test_default_reads_only_the_html_post(monkeypatch):
    calls = _fake_feed(monkeypatch, [_story(str(i), 1000 - i) for i in range(5)])
    posts = FacebookPageScraper.PagePostInfo("example")
    assert [p["id"] for p in posts] == ["0"]
    assert calls == []


def test_max_posts_none_walks_back_to_the_first_post(monkeypatch):
    timeline = [_story(str(i), 1000 - i) for i in range(95)]
    calls = _fake_feed(monkeypatch, timeline)
    posts = FacebookPageScraper.PagePostInfo("example", max_posts=None)
    assert [p["id"] for p in posts] == [p["post_id"] for p in timeline]
    assert all(c["count"] == page_post_info.PAGE_SIZE for c in calls)
    assert calls[0]["beforeTime"] == 1000


def test_max_posts_and_since_stop_early(monkeypatch):
    timeline = [_story(str(i), 1000 - i) for i in range(95)]
    _fake_feed(monkeypatch, timeline)
    assert len(FacebookPageScraper.PagePostInfo("example", max_posts=50)) == 50
    posts = FacebookPageScraper.PagePostInfo("example", max_posts=None, since=950)
    assert [p["creation_time"] for p in posts] == list(range(1000, 949, -1))


def test_failed_feed_request_keeps_posts_so_far(monkeypatch):
    _fake_feed(monkeypatch, [_story(str(i), 1000 - i) for i in range(5)])
    monkeypatch.setattr(RequestHandler, "post_graphql", lambda *a, **k: None)
    assert [p["id"] for p in FacebookPageScraper.PagePostInfo("example", max_posts=None)] == ["0"]


def test_since_accepts_dates_and_strings():
    assert page_post_info._unix("2026-01-01") == 1767225600
    assert page_post_info._unix(page_post_info.date(2026, 1, 1)) == 1767225600
    assert page_post_info._unix(1767225600) == 1767225600
