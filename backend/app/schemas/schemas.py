"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ─── Auth ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    role: str
    created_at: datetime


# ─── Show ───────────────────────────────────────────────────────────────────

class ShowCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    synopsis: Optional[str] = ""
    category: str = Field(min_length=1, max_length=100)
    section: Optional[str] = ""
    status: str = Field(default="draft", pattern="^(draft|published)$")


class ShowUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    synopsis: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    section: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")


class ArtworkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    type: str
    storage_key: str
    width: int
    height: int
    size_bytes: int
    created_at: datetime


class EpisodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    season_id: UUID
    episode_number: int
    title: str
    description: Optional[str] = ""
    duration: Optional[int] = None
    content_group: str
    language: str
    status: str
    created_at: datetime
    updated_at: datetime
    artwork: list[ArtworkOut] = []


class SeasonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    show_id: UUID
    season_number: int
    title: str
    episodes: list[EpisodeOut] = []


class ShowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    synopsis: Optional[str] = ""
    category: str
    section: Optional[str] = ""
    status: str
    created_at: datetime
    updated_at: datetime
    seasons: list[SeasonOut] = []
    artwork: list[ArtworkOut] = []


class ShowListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    category: str
    section: Optional[str] = ""
    status: str
    updated_at: datetime
    season_count: int = 0
    episode_count: int = 0


class ShowListResponse(BaseModel):
    items: list[ShowListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ─── Season ─────────────────────────────────────────────────────────────────

class SeasonCreate(BaseModel):
    season_number: int = Field(ge=0)
    title: str = Field(min_length=1, max_length=500)


class SeasonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    season_number: Optional[int] = Field(None, ge=0)


# ─── Episode ────────────────────────────────────────────────────────────────

class EpisodeCreate(BaseModel):
    episode_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = ""
    duration: Optional[int] = Field(None, ge=1)
    content_group: str = Field(min_length=1, max_length=255)
    language: str = Field(min_length=1, max_length=50)
    status: str = Field(default="draft", pattern="^(draft|published)$")


class EpisodeUpdate(BaseModel):
    episode_number: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    duration: Optional[int] = Field(None, ge=1)
    content_group: Optional[str] = Field(None, min_length=1, max_length=255)
    language: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[str] = Field(None, pattern="^(draft|published)$")


# ─── Validation Report ──────────────────────────────────────────────────────

class ValidationError(BaseModel):
    entity: str
    entity_id: Optional[str] = None
    entity_name: str
    field: str
    problem: str
    fix: str


class ValidationReport(BaseModel):
    blocking: bool
    total_errors: int
    shows: list[ValidationError] = []
    episodes: list[ValidationError] = []
    artwork: list[ValidationError] = []
    metadata: list[ValidationError] = []


# ─── Publish ────────────────────────────────────────────────────────────────

class PublishRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    triggered_by: UUID
    status: str
    shows_count: Optional[int] = 0
    episodes_count: Optional[int] = 0
    catalogue_key: Optional[str] = None
    error: Optional[str] = None


class PublishResponse(BaseModel):
    success: bool
    message: str
    publish_run: Optional[PublishRunOut] = None
    validation_report: Optional[ValidationReport] = None


# ─── Catalogue (Viewer) ────────────────────────────────────────────────────

class CatalogueEpisode(BaseModel):
    content_group: str
    episode_number: int
    title: str
    description: str
    duration: int
    languages: list[str]
    artwork: dict = {}


class CatalogueSeason(BaseModel):
    season_number: int
    title: str
    episodes: list[CatalogueEpisode]


class CatalogueTrailer(BaseModel):
    content_group: str
    title: str
    duration: int
    languages: list[str]
    artwork: dict = {}


class CatalogueShow(BaseModel):
    id: str
    title: str
    synopsis: str
    category: str
    artwork: dict = {}
    seasons: list[CatalogueSeason]
    trailers: list[CatalogueTrailer] = []


class CatalogueSection(BaseModel):
    name: str
    shows: list[CatalogueShow]


class Catalogue(BaseModel):
    version: str
    published_at: str
    sections: list[CatalogueSection]


# ─── Health ─────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    database: str
    storage: str


# ─── Pagination ─────────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = None
    section: Optional[str] = None
    status: Optional[str] = None
    language: Optional[str] = None
