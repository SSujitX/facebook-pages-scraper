## Learned User Preferences

- Prefer packaging like google-news-url-decoder: single version in `pyproject.toml`, runtime via `importlib.metadata`; no `__version__.py` and no `setup.py`.
- Prefer the modern `.github/workflows/publish.yml` release flow over the older `python-publish.yml`.
- Prefer `page_social_accounts` as a network→URL map (e.g. Instagram → link), not bare handles or separate network/url fields.
- Want PageInfo to cover About-tab richness: short intro, longer about/details, structured socials, transparency (page id + creation date), and full weekly hours when available.

## Learned Workspace Facts

- Distribution/PyPI name is `facebook-pages-scraper`; import package is `facebook_page_scraper`; public class is `FacebookPageScraper` (uv `module-name` must match the import package, not the class name).
- Packaging is uv/`pyproject.toml`-based; `__version__` comes from installed package metadata.
- Page HTML embeds data in `application/json` scripts (`profile_tile_items` / intro cards); many About fields live on about endpoints (`/about_contact_and_basic_info`, `/about_details`, `/about_profile_transparency`), not the main profile document alone.
- Intro address cards can have `"title": null` (deferred modules); parsers must skip null titles or the whole intro path fails.
- Public profile HTML often no longer exposes page likes / likes counts.
- `page_intro` is the short tagline under the name; `page_about` is the longer Details About text from the About tab.
