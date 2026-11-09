# AVRWIBUID — Multi-source anime catalog starter

## Backend
```bash
cd backend
python -m venv .venv
# activate environment, then:
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
For local development, SQLite is used if `DATABASE_URL` is not set.
For deployment, configure a PostgreSQL URL and a strong `ADMIN_TOKEN`.

## Frontend
```bash
cd frontend
npm install
# frontend/.env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
npm run dev
```

## Configure authorized metadata sources
Set `SCRAPE_SOURCES_JSON` to a JSON array. Each source needs:
`name`, `base_url`, `listing_url`, and optional CSS `selectors`.
Only crawl sources that permit automated access. The scraper checks HTTPS,
same-host URLs, and robots.txt, uses a delay between sources, and does not
extract video files or bypass access controls.

Example (replace with a source you own or are authorized to crawl):
```json
[
  {
    "name": "authorized-catalog",
    "base_url": "https://catalog.example.org",
    "listing_url": "https://catalog.example.org/anime",
    "selectors": {
      "items": "article.anime-card",
      "title": "h2 a",
      "poster": "img",
      "detail_link": "h2 a"
    }
  }
]
```

## Admin sync
`POST /api/admin/sync` with header `X-Admin-Token: <ADMIN_TOKEN>`.
The scheduler also runs every 6 hours while the backend process is alive.
For production, run the worker as a dedicated always-on service, not inside a
short-lived serverless function.

## Streaming
The episode endpoint is a placeholder. Configure a video provider only when
you have permission to embed or distribute its streams. AniList metadata is
used as a catalog fallback until authorized HTML sources are configured.


## Single video player and auto-next
The watch page uses one player instance per selected episode. It supports:
- Direct MP4/file URLs from an authorized provider.
- HLS `.m3u8` streams through `hls.js`.
- Authorized iframe embeds with a server selector.
- Episode navigation and Auto Next.

For iframe embeds, the provider page must send this completion event to its parent:
```js
window.parent.postMessage({ type: "AVRWIBUID_EPISODE_ENDED" }, "https://your-avrwibuid-domain.example");
```
The player checks `event.origin` against the selected provider URL before advancing.
Auto-next for iframe embeds will not work unless the provider explicitly supports this event.
Direct video playback uses the browser's `ended` event.

Configure `STREAM_ALLOWED_HOSTS` as a comma-separated list of exact HTTPS hostnames.
Admin API:
- `POST /api/admin/anime/{anime_id}/episodes`
- `POST /api/admin/episodes/{episode_id}/streams`
- `GET /api/admin/sources`

Send `X-Admin-Token` with every admin request. Keep this token private.
The database schema changed for episode/provider tables. For an existing development database,
back it up and recreate it for this starter, or add Alembic migrations before production use.
