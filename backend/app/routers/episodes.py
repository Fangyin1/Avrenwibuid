from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Anime, Episode, StreamProvider

router = APIRouter()

@router.get("/{anime_id}")
async def list_episodes(anime_id: int, db: AsyncSession = Depends(get_db)):
    anime_result = await db.execute(select(Anime).where(Anime.id == anime_id))
    if anime_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Anime tidak ditemukan")
    result = await db.execute(
        select(Episode).where(Episode.anime_id == anime_id).order_by(Episode.episode_number.asc())
    )
    episodes = result.scalars().all()
    output = []
    for ep in episodes:
        stream_result = await db.execute(
            select(StreamProvider).where(
                StreamProvider.episode_id == ep.id, StreamProvider.enabled.is_(True)
            ).order_by(StreamProvider.id.asc())
        )
        streams = stream_result.scalars().all()
        output.append({
            "id": ep.id,
            "episode_number": ep.episode_number,
            "title": ep.title,
            "streams": [
                {"id": s.id, "label": s.label, "kind": s.kind, "url": s.url, "mime_type": s.mime_type}
                for s in streams
            ],
        })
    return {"anime_id": anime_id, "episodes": output}
