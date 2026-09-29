"""Turn a username or any facebook.com host into https://www.facebook.com/<page>."""


def normalize_url(input_url: str) -> str:
    raw = input_url.strip()
    lower = raw.lower()
    if "facebook.com" in lower:
        if "://" not in raw:
            raw = "https://" + raw
            lower = raw.lower()
        path = raw.split("://", 1)[1]
        path = path.split("/", 1)[1] if "/" in path else ""
        path = path.split("?", 1)[0].split("#", 1)[0].strip("/")
        return "https://www.facebook.com/" + path
    path = raw.lstrip("/").split("?", 1)[0].split("#", 1)[0].strip("/")
    return "https://www.facebook.com/" + path
