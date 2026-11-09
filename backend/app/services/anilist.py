import httpx

ANILIST_URL = "https://graphql.anilist.co"

async def _query(query: str, variables: dict | None = None):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            ANILIST_URL,
            json={"query": query, "variables": variables or {}},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise RuntimeError("AniList API returned an error")
        return payload["data"]

def normalize(media: dict) -> dict:
    title = media.get("title") or {}
    cover = media.get("coverImage") or {}
    return {
        "id": media["id"],
        "title": title.get("english") or title.get("romaji") or title.get("native"),
        "romaji": title.get("romaji"),
        "description": media.get("description"),
        "cover": cover.get("extraLarge") or cover.get("large"),
        "banner": media.get("bannerImage"),
        "episodes": media.get("episodes"),
        "status": media.get("status"),
        "season": media.get("season"),
        "seasonYear": media.get("seasonYear"),
        "genres": media.get("genres") or [],
        "averageScore": media.get("averageScore"),
        "format": media.get("format"),
    }

TRENDING_QUERY = """
query {
  Page(perPage: 24) {
    media(type: ANIME, sort: TRENDING_DESC) {
      id
      title { romaji english native }
      description(asHtml: false)
      coverImage { large extraLarge }
      bannerImage
      episodes
      status
      season
      seasonYear
      genres
      averageScore
      format
    }
  }
}
"""

DETAIL_QUERY = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    id
    title { romaji english native }
    description(asHtml: false)
    coverImage { large extraLarge }
    bannerImage
    episodes
    status
    season
    seasonYear
    genres
    averageScore
    format
  }
}
"""

SEARCH_QUERY = """
query ($search: String) {
  Page(perPage: 24) {
    media(search: $search, type: ANIME, sort: SEARCH_MATCH) {
      id
      title { romaji english native }
      description(asHtml: false)
      coverImage { large extraLarge }
      bannerImage
      episodes
      status
      season
      seasonYear
      genres
      averageScore
      format
    }
  }
}
"""

async def fetch_trending():
    data = await _query(TRENDING_QUERY)
    return [normalize(x) for x in data["Page"]["media"]]

async def fetch_anime_detail(anime_id: int):
    data = await _query(DETAIL_QUERY, {"id": anime_id})
    media = data.get("Media")
    return normalize(media) if media else None

async def search_anime(term: str):
    data = await _query(SEARCH_QUERY, {"search": term})
    return [normalize(x) for x in data["Page"]["media"]]
