"""Initial schema - all tables

Revision ID: 001_initial
Revises: None
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = postgresql.ENUM("editor", "admin", name="user_role", create_type=False)
    content_status = postgresql.ENUM("draft", "published", name="content_status", create_type=False)
    artwork_type = postgresql.ENUM("poster", "banner", "thumbnail", name="artwork_type", create_type=False)
    publish_status = postgresql.ENUM("running", "success", "failed", "blocked", name="publish_status", create_type=False)

    user_role.create(op.get_bind(), checkfirst=True)
    content_status.create(op.get_bind(), checkfirst=True)
    artwork_type.create(op.get_bind(), checkfirst=True)
    publish_status.create(op.get_bind(), checkfirst=True)

    # Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="editor"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # Shows
    op.create_table(
        "shows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("synopsis", sa.Text, nullable=True, server_default=""),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("section", sa.String(100), nullable=True, server_default=""),
        sa.Column("status", content_status, nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_shows_title", "shows", ["title"])
    op.create_index("ix_shows_category", "shows", ["category"])
    op.create_index("ix_shows_section", "shows", ["section"])
    op.create_index("ix_shows_status", "shows", ["status"])

    # Seasons
    op.create_table(
        "seasons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("show_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shows.id", ondelete="CASCADE"), nullable=False),
        sa.Column("season_number", sa.Integer, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
    )
    op.create_index("ix_seasons_show_id", "seasons", ["show_id"])
    op.create_unique_constraint("uq_season_show_number", "seasons", ["show_id", "season_number"])

    # Episodes
    op.create_table(
        "episodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("season_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("episode_number", sa.Integer, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True, server_default=""),
        sa.Column("duration", sa.Integer, nullable=True),
        sa.Column("content_group", sa.String(255), nullable=False),
        sa.Column("language", sa.String(50), nullable=False),
        sa.Column("status", content_status, nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_episodes_season_id", "episodes", ["season_id"])
    op.create_index("ix_episodes_title", "episodes", ["title"])
    op.create_index("ix_episodes_content_group", "episodes", ["content_group"])
    op.create_index("ix_episodes_language", "episodes", ["language"])
    op.create_index("ix_episodes_status", "episodes", ["status"])
    op.create_unique_constraint("uq_episode_content_group_language", "episodes", ["content_group", "language"])

    # Artwork
    op.create_table(
        "artwork",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("show_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shows.id", ondelete="CASCADE"), nullable=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE"), nullable=True),
        sa.Column("type", artwork_type, nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("width", sa.Integer, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
        sa.Column("size_bytes", sa.BigInteger, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_artwork_show_id", "artwork", ["show_id"])
    op.create_index("ix_artwork_episode_id", "artwork", ["episode_id"])
    op.create_index("ix_artwork_type", "artwork", ["type"])

    # Publish Runs
    op.create_table(
        "publish_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", publish_status, nullable=False, server_default="running"),
        sa.Column("shows_count", sa.Integer, nullable=True, server_default="0"),
        sa.Column("episodes_count", sa.Integer, nullable=True, server_default="0"),
        sa.Column("catalogue_key", sa.String(500), nullable=True),
        sa.Column("error", sa.Text, nullable=True),
    )
    op.create_index("ix_publish_runs_status", "publish_runs", ["status"])
    op.create_index("ix_publish_runs_started_at", "publish_runs", ["started_at"])


def downgrade() -> None:
    op.drop_table("publish_runs")
    op.drop_table("artwork")
    op.drop_table("episodes")
    op.drop_table("seasons")
    op.drop_table("shows")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS publish_status")
    op.execute("DROP TYPE IF EXISTS artwork_type")
    op.execute("DROP TYPE IF EXISTS content_status")
    op.execute("DROP TYPE IF EXISTS user_role")
