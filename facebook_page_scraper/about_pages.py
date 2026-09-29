"""Fields that live on the About tab, not the main profile HTML."""

from typing import Dict, Optional

from .facebook_json import about_body, field_text


def _load(handler, page_url: str, path: str, marker: str):
    html = handler.fetch_html(page_url.rstrip("/") + path)
    return handler.find_json(html, marker)


def about_address(handler, page_url: str) -> Optional[str]:
    data = _load(handler, page_url, "/about_contact_and_basic_info", '"field_type":"address"')
    if not data:
        return None
    return field_text(data, "address")


def about_text(handler, page_url: str) -> Optional[str]:
    data = _load(handler, page_url, "/about_details", '"field_type":"about_me"')
    if not data:
        return None
    return about_body(data)


def transparency(handler, page_url: str) -> Dict[str, Optional[str]]:
    data = _load(handler, page_url, "/about_profile_transparency", '"field_type":"creation_date"')
    if not data:
        return {}
    return {
        "page_id": field_text(data, "page_id"),
        "page_creation_date": field_text(data, "creation_date"),
    }


async def _load_async(handler, page_url: str, path: str, marker: str):
    html = await handler.fetch_html(page_url.rstrip("/") + path)
    return handler.find_json(html, marker)


async def about_address_async(handler, page_url: str) -> Optional[str]:
    data = await _load_async(handler, page_url, "/about_contact_and_basic_info", '"field_type":"address"')
    if not data:
        return None
    return field_text(data, "address")


async def about_text_async(handler, page_url: str) -> Optional[str]:
    data = await _load_async(handler, page_url, "/about_details", '"field_type":"about_me"')
    if not data:
        return None
    return about_body(data)


async def transparency_async(handler, page_url: str) -> Dict[str, Optional[str]]:
    data = await _load_async(handler, page_url, "/about_profile_transparency", '"field_type":"creation_date"')
    if not data:
        return {}
    return {
        "page_id": field_text(data, "page_id"),
        "page_creation_date": field_text(data, "creation_date"),
    }
