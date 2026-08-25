"""Tests for authorization enforcement."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4

from fastapi import HTTPException
from app.auth.auth import require_role


class TestRoleAuthorization:
    """Tests for role-based access control."""

    @pytest.mark.asyncio
    async def test_editor_cannot_publish(self):
        """An editor should receive 403 when trying to publish."""
        checker = require_role("admin")

        editor = MagicMock()
        editor.role = "editor"
        editor.id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await checker(current_user=editor)

        assert exc_info.value.status_code == 403
        assert "admin" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_admin_can_publish(self):
        """An admin should pass the admin role check."""
        checker = require_role("admin")

        admin = MagicMock()
        admin.role = "admin"
        admin.id = uuid4()

        result = await checker(current_user=admin)
        assert result == admin

    @pytest.mark.asyncio
    async def test_editor_can_access_editor_routes(self):
        """An editor should pass the editor role check."""
        checker = require_role("editor")

        editor = MagicMock()
        editor.role = "editor"
        editor.id = uuid4()

        result = await checker(current_user=editor)
        assert result == editor

    @pytest.mark.asyncio
    async def test_admin_can_access_editor_routes(self):
        """An admin should also pass the editor role check (hierarchy)."""
        checker = require_role("editor")

        admin = MagicMock()
        admin.role = "admin"
        admin.id = uuid4()

        result = await checker(current_user=admin)
        assert result == admin
