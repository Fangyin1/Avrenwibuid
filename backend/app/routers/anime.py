from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Anime
from app.services.anilist import fetch_trending, fetch_anime_detail, search_anime

router = APIRouter()

@router.get("/")
async def list_catalog(q: str | None = None, limit: int = Query(40, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    if q:
        result = await db.execute(select(Anime).where(Anime.title.ilike(f"%{q}%")).limit(limit))
    else:
        result = await db.execute(select(Anime).order_by(Anime.updated_at.desc()).limit(limit))
    rows = result.scalars().all()
    if rows:
        return [{"id": x.id, "title": x.title, "cover": x.poster_url, "description": x.synopsis, "status": x.status} for x in rows]
    # Metadata fallback keeps the site useful before an authorized scraper source is configured.
    return await search_anime(q) if q else await fetch_trending()

@router.get("/trending")
async def trending():
    return await fetch_trending()

@router.get("/search")
async def search(q: str = Query(min_length=1, max_length=100)):
    return await search_anime(q)

@router.get("/{anime_id}")
async def detail(anime_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Anime).where(Anime.id == anime_id))
    anime = result.scalar_one_or_none()
    if anime:
        return {"id": anime.id, "title": anime.title, "cover": anime.poster_url, "description": anime.synopsis, "status": anime.status}
    data = await fetch_anime_detail(anime_id)
    if not data:
        raise HTTPException(status_code=404, detail="Anime tidak ditemukan")
    return data
