"""
Source definitions are deliberately configuration-driven.
Only add domains you own or are authorized to crawl. Respect the site's
terms, robots.txt, rate limits, and attribution requirements.

Example environment variable:
SCRAPE_SOURCES_JSON=[
 {"name":"my-authorized-catalog","base_url":"https://example.org",
  "listing_url":"https://example.org/anime",
  "selectors":{"items":"article.anime-card","title":"h2 a",
  "poster":"img","detail_link":"h2 a"}}
]
"""
import json, os

def load_sources():
    raw = os.getenv("SCRAPE_SOURCES_JSON", "[]")
    try:
        sources = json.loads(raw)
        if not isinstance(sources, list):
            raise ValueError("SCRAPE_SOURCES_JSON must be a JSON array")
        return [s for s in sources if s.get("name") and s.get("base_url") and s.get("listing_url")]
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"Invalid SCRAPE_SOURCES_JSON: {exc}") from exc
