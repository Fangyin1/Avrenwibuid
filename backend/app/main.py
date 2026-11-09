from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import anime, episodes, admin
from app.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="AVRWIBUID API", version="2.0.0", lifespan=lifespan)
origins = [x.strip() for x in __import__("os").getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(anime.router, prefix="/api/anime", tags=["anime"])
app.include_router(episodes.router, prefix="/api/episodes", tags=["episodes"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AVRWIBUID API", "version": "2.0.0"}
