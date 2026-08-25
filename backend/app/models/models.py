"""SQLAlchemy models for Peblo TV Mini."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    Enum as SAEnum,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


def new_uuid():
    return uuid.uuid4()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum("editor", "admin", name="user_role"), nullable=False, default="editor")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class Show(Base):
    __tablename__ = "shows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    title = Column(String(500), nullable=False, index=True)
    synopsis = Column(Text, nullable=True, default="")
    category = Column(String(100), nullable=False)
    section = Column(String(100), nullable=True, default="")
    status = Column(
        SAEnum("draft", "published", name="content_status"),
        nullable=False,
        default="draft",
    )
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    seasons = relationship("Season", back_populates="show", cascade="all, delete-orphan", order_by="Season.season_number")
    artwork = relationship("Artwork", back_populates="show", cascade="all, delete-orphan",
                          primaryjoin="and_(Show.id==Artwork.show_id, Artwork.episode_id==None)")

    __table_args__ = (
        Index("ix_shows_category", "category"),
        Index("ix_shows_section", "section"),
        Index("ix_shows_status", "status"),
    )


class Season(Base):
    __tablename__ = "seasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    show_id = Column(UUID(as_uuid=True), ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    season_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)

    # Relationships
    show = relationship("Show", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan", order_by="Episode.episode_number")

    __table_args__ = (
        UniqueConstraint("show_id", "season_number", name="uq_season_show_number"),
        Index("ix_seasons_show_id", "show_id"),
    )


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    season_id = Column(UUID(as_uuid=True), ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True, default="")
    duration = Column(Integer, nullable=True)  # seconds
    content_group = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(
        SAEnum("draft", "published", name="content_status", create_type=False),
        nullable=False,
        default="draft",
    )
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    season = relationship("Season", back_populates="episodes")
    artwork = relationship("Artwork", back_populates="episode", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("content_group", "language", name="uq_episode_content_group_language"),
        Index("ix_episodes_season_id", "season_id"),
        Index("ix_episodes_content_group", "content_group"),
        Index("ix_episodes_language", "language"),
        Index("ix_episodes_status", "status"),
    )


class Artwork(Base):
    __tablename__ = "artwork"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    show_id = Column(UUID(as_uuid=True), ForeignKey("shows.id", ondelete="CASCADE"), nullable=True)
    episode_id = Column(UUID(as_uuid=True), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=True)
    type = Column(
        SAEnum("poster", "banner", "thumbnail", name="artwork_type"),
        nullable=False,
    )
    storage_key = Column(String(500), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Relationships
    show = relationship("Show", back_populates="artwork", foreign_keys=[show_id])
    episode = relationship("Episode", back_populates="artwork", foreign_keys=[episode_id])

    __table_args__ = (
        Index("ix_artwork_show_id", "show_id"),
        Index("ix_artwork_episode_id", "episode_id"),
        Index("ix_artwork_type", "type"),
    )


class PublishRun(Base):
    __tablename__ = "publish_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    started_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(
        SAEnum("running", "success", "failed", "blocked", name="publish_status"),
        nullable=False,
        default="running",
    )
    shows_count = Column(Integer, nullable=True, default=0)
    episodes_count = Column(Integer, nullable=True, default=0)
    catalogue_key = Column(String(500), nullable=True)
    error = Column(Text, nullable=True)

    # Relationships
    user = relationship("User")

    __table_args__ = (
        Index("ix_publish_runs_status", "status"),
        Index("ix_publish_runs_started_at", "started_at"),
    )
