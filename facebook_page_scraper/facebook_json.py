"""Small lookups into the JSON Facebook embeds in the page HTML."""

from typing import Optional


def relay_results(json_data: dict):
    """Yield each prefetched Relay result inside a script JSON blob."""
    requires = json_data.get("require", [])
    if not requires:
        raise ValueError("Missing 'require' key in JSON data.")
    requires = requires[0][3][0].get("__bbox", {}).get("require", [])
    for require in requires:
        if "RelayPrefetchedStreamCache" in require:
            yield require[3][1].get("__bbox", {}).get("result", {})


def text_at(obj, key: str) -> Optional[str]:
    """First `{key: {"text": "..."}}` found anywhere under obj."""
    if isinstance(obj, dict):
        value = obj.get(key)
        if isinstance(value, dict) and isinstance(value.get("text"), str):
            return value["text"]
        for child in obj.values():
            found = text_at(child, key)
            if found:
                return found
    elif isinstance(obj, list):
        for child in obj:
            found = text_at(child, key)
            if found:
                return found
    return None


def field_text(obj, field_type: str) -> Optional[str]:
    """Title text of the About field whose field_type matches."""
    if isinstance(obj, dict):
        if obj.get("field_type") == field_type:
            title = obj.get("title") or {}
            text = title.get("text") if isinstance(title, dict) else None
            if text:
                return text
        for value in obj.values():
            found = field_text(value, field_type)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = field_text(value, field_type)
            if found:
                return found
    return None


def about_body(obj) -> Optional[str]:
    """Paragraph under the about_me field, not the 'About {name}' heading."""
    if isinstance(obj, dict):
        kind = obj.get("field_type") or obj.get("field_section_type")
        if kind == "about_me":
            text = _long_text(obj)
            if text:
                return text
        for value in obj.values():
            found = about_body(value)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = about_body(value)
            if found:
                return found
    return None


def _long_text(obj) -> Optional[str]:
    if isinstance(obj, dict):
        content = obj.get("text_content")
        title = obj.get("title")
        title_text = title.get("text") if isinstance(title, dict) else None
        if isinstance(content, dict) and isinstance(content.get("text"), str):
            text = content["text"].strip()
            if text and text != title_text:
                return text
        for value in obj.values():
            found = _long_text(value)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _long_text(value)
            if found:
                return found
    return None
