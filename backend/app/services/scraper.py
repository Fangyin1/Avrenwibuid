from __future__ import annotations
import asyncio, hashlib, json, re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Anime, ScrapeSource
from app.services.source_config import load_sources

USER_AGENT = "AVRWIBUIDCatalogBot/1.0 (+contact: site-admin; respectful metadata crawler)"
TIMEOUT = 20
DELAY_SECONDS = 3

def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", value).strip() or None

def canonical_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:500]

def allowed_url(url: str, base_url: str) -> bool:
    parsed, base = urlparse(url), urlparse(base_url)
    return parsed.scheme == "https" and parsed.netloc == base.netloc

async def robots_allows(client: httpx.AsyncClient, url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        response = await client.get(robots_url)
        if response.status_code == 404:
            return True
        response.raise_for_status()
        from urllib.robotparser import RobotFileParser
        parser = RobotFileParser()
        parser.parse(response.text.splitlines())
        return parser.can_fetch(USER_AGENT, url)
    except httpx.HTTPError:
        # Fail closed if the site's crawler policy cannot be checked.
        return False

def extract_items(html: str, source: dict) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    selectors = source.get("selectors", {})
    item_selector = selectors.get("items", "article")
    title_selector = selectors.get("title", "h2 a")
    poster_selector = selectors.get("poster", "img")
    link_selector = selectors.get("detail_link", "a")
    results = []
    for card in soup.select(item_selector)[:100]:
        title_el = card.select_one(title_selector)
        link_el = card.select_one(link_selector)
        image_el = card.select_one(poster_selector)
        title = clean_text(title_el.get_text(" ", strip=True) if title_el else None)
        href = link_el.get("href") if link_el else None
        poster = None
        if image_el:
            poster = image_el.get("data-src") or image_el.get("src")
        if title and href:
            results.append({
                "title": title,
                "page_url": urljoin(source["base_url"], href),
                "poster_url": urljoin(source["base_url"], poster) if poster else None,
            })
    return results

async def sync_one_source(db: AsyncSession, client: httpx.AsyncClient, source: dict) -> dict:
    listing_url = source["listing_url"]
    if not allowed_url(listing_url, source["base_url"]):
        return {"source": source["name"], "status": "rejected", "reason": "Listing URL must be HTTPS on configured host"}
    if not await robots_allows(client, listing_url):
        return {"source": source["name"], "status": "skipped", "reason": "robots.txt disallows crawling or policy unavailable"}
    response = await client.get(listing_url)
    response.raise_for_status()
    items = extract_items(response.text, source)
    saved = 0
    for item in items:
        if not allowed_url(item["page_url"], source["base_url"]):
            continue
        key = canonical_key(item["title"])
        result = await db.execute(select(Anime).where(Anime.canonical_key == key))
        anime = result.scalar_one_or_none()
        if anime is None:
            anime = Anime(canonical_key=key, title=item["title"])
            db.add(anime)
        # Do not overwrite richer metadata with empty values.
        if item.get("poster_url"):
            anime.poster_url = item["poster_url"]
        saved += 1
    await db.commit()
    return {"source": source["name"], "status": "ok", "items_seen": len(items), "items_processed": saved}

async def sync_all_sources(db: AsyncSession) -> list[dict]:
    sources = load_sources()
    results = []
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=headers, follow_redirects=True) as client:
        for source in sources:
            started = datetime.now(timezone.utc)
            try:
                result = await sync_one_source(db, client, source)
            except Exception as exc:
                await db.rollback()
                result = {"source": source["name"], "status": "error", "reason": str(exc)[:300]}
            source_row_result = await db.execute(
                select(ScrapeSource).where(ScrapeSource.name == source["name"])
            )
            source_row = source_row_result.scalar_one_or_none()
            if source_row is None:
                source_row = ScrapeSource(name=source["name"], base_url=source["base_url"])
                db.add(source_row)
            source_row.base_url = source["base_url"]
            source_row.enabled = source.get("enabled", True)
            source_row.last_status = result["status"]
            source_row.last_message = result.get("reason")
            source_row.last_run_at = started
            source_row.items_seen = result.get("items_seen", 0)
            await db.commit()
            results.append(result)
            await asyncio.sleep(DELAY_SECONDS)
    return results
