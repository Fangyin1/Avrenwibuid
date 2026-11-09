from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Literal

class AnimeOut(BaseModel):
    id: int
    title: str
    synopsis: Optional[str] = None
    poster_url: Optional[str] = None
    status: Optional[str] = None
    year: Optional[int] = None
    class Config:
        from_attributes = True

class SourceCreate(BaseModel):
    name: str
    base_url: HttpUrl
    listing_url: HttpUrl
    enabled: bool = True

class EpisodeCreate(BaseModel):
    episode_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=500)

class StreamCreate(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    kind: Literal["embed", "file"]
    url: HttpUrl
    mime_type: Optional[str] = None
