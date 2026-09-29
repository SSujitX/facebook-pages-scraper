## Learned User Preferences

- Prefer packaging like google-news-url-decoder: single version in `pyproject.toml`, runtime via `importlib.metadata`; no `__version__.py` and no `setup.py`.
- Release workflow is `.github/workflows/python-publish.yml`. PyPI trusted publishing is bound to that path. Do not rename the file unless the publisher is updated to match.
- Prefer `page_social_accounts` as a network→URL map (e.g. Instagram → link), not bare handles or separate network/url fields.
- Want PageInfo to cover About-tab richness: short intro, longer about/details, structured socials, transparency (page id + creation date), and full weekly hours when the HTML actually contains them.

## Learned Workspace Facts

- Distribution/PyPI name is `facebook-pages-scraper`; import package is `facebook_page_scraper`; public class is `FacebookPageScraper`. uv `module-name` must be the import package, not the class name.
- `__version__` is `importlib.metadata.version("facebook-pages-scraper")`. It only works after the package is installed (`uv sync`).
- Public calls stay PascalCase: `PageInfo`, `PageInfoAsync`, `PagePostInfo`, `PagePostInfoAsync`. A string returns one result. A list returns one result per page, in order. A failed page is `None`. One `proxy` covers the whole call. Async list concurrency defaults to 4.
- Do not rotate User-Agent. `curl_cffi` `Session` / `AsyncSession(impersonate="chrome")` plus `accept-language` is the client. A custom UA fights the TLS fingerprint. One session per page so cookies persist. `proxy=None` means direct. Pass `http://`, `https://`, or `socks5://` through `proxy=`. No PySocks dependency.
- `fetch_html` returns `None` on HTTP or network failure. It must not call `sys.exit`. Sync scrapes that create their own handler close it in `finally`. Async creates one `AsyncRequestHandler` per URL and closes it in `finally`.
- PageInfo returns `None` unless both `username_for_profile` and `profile_tile_items` scripts are found. PagePostInfo returns `None` unless `timeline_list_feed_units` is found. An empty post list is a real result; `None` means the page failed.
- `urls.normalize_url` turns a username or any `facebook.com` host (`www`, `web`, `m`, `mbasic`) into `https://www.facebook.com/<path>` and strips query and hash. Responses may still redirect to `web.facebook.com`.
- `pizzaburgbd` is the full-field check page (intro, about, address, phone, email, website, hours line, services, Instagram, owner, page id, creation date). `bbcnews` often has no `about_me`, so an empty `page_about` there is not a parser bug. Offline checks: `uv run pytest` (`tests/test_contract.py`). The other files under `tests/` are live examples.

## How a scrape works

1. `normalize_url`, then one Chrome session fetches `https://www.facebook.com/<page>`.
2. `find_json` returns the first `script[type=application/json]` whose text contains the marker. `facebook_json.relay_results` walks `require` → `RelayPrefetchedStreamCache` → `result`. A missing `require` raises `ValueError`, which the extractors catch and print.
3. Header JSON marker `username_for_profile`: name, url, pics, cover, `delegate_page.id` (page id), business flag, followers text. `page_likes` is filled only when a `friends_likes` URI is present. Do not copy followers into likes.
4. Intro JSON marker `profile_tile_items`. Cards map by `timeline_context_list_item_type` to category, address, phone, email, website, hours, price, rating, services, socials, owner. A null `title` is skipped (`title or {}`, then require a dict). `INTRO_CARD_OTHER_ACCOUNT` stores `page_social_accounts[network] = external_url` (duplicate network overwrites). Owner becomes `"NAME is responsible for this Page"` when a subtitle exists.
5. `page_intro` is `best_description` text from the main HTML. `page_about` is the about_me body from `/about_details` (`text_content`, not the "About {name}" heading). If the intro address is empty, `/about_contact_and_basic_info` supplies `field_type` `address`. `/about_profile_transparency` overwrites `page_id` when present and sets `page_creation_date`. Those three About fetches are `fatal`-free (a miss leaves the field empty). Async runs them with `asyncio.gather` on the same session after the main parse.
6. Meta description regex fills `page_likes_count`, `page_talking_count`, `page_were_here_count` only when those phrases exist.
7. Posts: marker `timeline_list_feed_units`. The first HTML document contains only the latest post (preload count is 1). Fields: `post_id` or `id`, `permalink_url`, unix `creation_time`, message text via the comet message path, `reaction_count.count`, `comments.total_count`, `share_count.count`. Single photos are `styles.attachment.media.photo_image` (also `viewer_image`, `image`, `playable_url`, `browser_native_sd_url`). Albums are `all_subattachments`. There is no pagination; the doc id for the next page is not in the HTML.

## When a field is missing

- Whole result `None`, and the log says the fetch failed: network, block, or bad URL. Check the normalized URL and proxy. Do not bring back `sys.exit`.
- Whole result `None`, and the log says no valid data: the HTML arrived but the marker script is gone (login wall or layout change). Search the saved HTML for the marker before changing the parser.
- One field `None` while the page dict exists: that card or About field is absent for this page. Confirm with a count of the marker (`about_me`, `friends_likes`, `INTRO_CARD_*`) in the HTML. `bbcnews` has no about_me. Most public pages have no likes string.
- `page_business_hours` is only the open/closed line Facebook embeds (`Open now`). The Monday–Sunday grid and popular times are not in the main page, `/about`, `/about_contact_and_basic_info`, or `/about_details`. A hours dialog script is referenced, but its doc id is not in the HTML. Do not invent a weekly table.
- Address looks doubled (city or postal code repeated): that string is what the About field title contains. Do not trim it unless the HTML itself has a cleaner field.
- Social map is `{}` when there is no other-account card. It is never `None`.
- Post `medias` empty on a single photo: read `photo_image`, not only `all_subattachments`.
- Only one post: expected. Do not add GraphQL pagination without a doc id taken from the HTML.
- `AttributeError` on `title.text`: an intro card has `"title": null` because `.get("title", {})` returns `None` when the key is present. Keep the null-safe title read.
- Windows console `UnicodeEncodeError`: post text can be non-cp1252. Print ids and lengths, not the raw text.
