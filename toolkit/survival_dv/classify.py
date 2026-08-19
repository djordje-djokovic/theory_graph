"""Fixed website classifier for Wayback snapshots and live pages."""

from __future__ import annotations

import re
import ssl
from typing import Optional

import requests
from bs4 import BeautifulSoup


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Parking / dead-page keywords. Comma bug in original is fixed: one keyword per line.
PARKING_KEYWORDS = [
    "domain", "for sale", "parked", "buy this domain", "is for sale",
    "godaddy", "sedo", "namecheap", "afternic", "dan.com", "parkingcrew",
    "this domain may be for sale", "domain owner", "related searches", "search results",
]

# Platforms that are NOT death if the page still resolves to them.
PLATFORM_HOSTS = {
    "wixsite.com", "wix.com", "wordpress.com", "squarespace.com", "webflow.com",
    "weebly.com", "blogspot.com", "tumblr.com", "github.io", "gitlab.io",
}

# Search engines that are NOT death if redirected to them.
SEARCH_HOSTS = {
    "google.com", "bing.com", "yahoo.com", "duckduckgo.com", "baidu.com",
}


def classify_page(url: str, html: Optional[str], final_url: Optional[str], status_code: int) -> dict:
    """Classify a fetched page as alive, dead, or inspect."""
    result = {
        "status_code": status_code,
        "final_url": final_url,
        "alive": False,
        "dead": False,
        "inspect": False,
        "reason": None,
    }

    if status_code == 403:
        result["inspect"] = True
        result["reason"] = "403_cloudflare"
        return result

    if status_code in (200, 301, 302, 307, 308):
        final_domain = _domain(final_url or url)
        if final_domain in SEARCH_HOSTS:
            result["alive"] = True
            result["reason"] = "search_redirect"
            return result
        if any(h in final_domain for h in PLATFORM_HOSTS):
            result["alive"] = True
            result["reason"] = "platform_host"
            return result

    if html and status_code in (200, 301, 302, 307, 308):
        text = BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True).lower()
        for kw in PARKING_KEYWORDS:
            if kw in text:
                result["dead"] = True
                result["reason"] = f"parking:{kw}"
                return result
        # If we got a real page with some content, call it alive
        if len(text.split()) >= 5:
            result["alive"] = True
            result["reason"] = "content"
            return result

    if status_code in (404, 410, 500, 503):
        result["dead"] = True
        result["reason"] = f"http_{status_code}"
        return result

    result["inspect"] = True
    result["reason"] = f"unhandled_status_{status_code}"
    return result


def fetch_page(url: str, timeout: int = 30) -> dict:
    """Fetch a live page and classify it, with SSL and error handling."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return classify_page(url, r.text, r.url, r.status_code)
    except requests.exceptions.SSLError:
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout, verify=False, allow_redirects=True)
            return classify_page(url, r.text, r.url, r.status_code)
        except Exception as e:
            return {"inspect": True, "reason": f"ssl_fetch_error:{type(e).__name__}", "alive": False, "dead": False}
    except requests.exceptions.RequestException as e:
        return {"inspect": True, "reason": f"request_error:{type(e).__name__}", "alive": False, "dead": False}


def _domain(url: str) -> str:
    if not url:
        return ""
    u = re.sub(r"^https?://", "", url.lower()).split("/")[0]
    return re.sub(r"^www\.", "", u)
