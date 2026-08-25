"""Storage abstraction layer.

Provides a clean interface for file storage operations.
Currently implements local filesystem storage.
To switch to Cloudflare R2 or S3, create a new class implementing
the same interface and swap via configuration.
"""

import os
import uuid
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import aiofiles


class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str = "") -> str:
        """Upload a file. Returns the storage key."""
        ...

    @abstractmethod
    async def get(self, key: str) -> Optional[bytes]:
        """Get file contents by key."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a file by key. Returns True if deleted."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a file exists."""
        ...

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Get the public URL for a file."""
        ...


class LocalStorage(StorageBackend):
    """Local filesystem storage implementation."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _full_path(self, key: str) -> Path:
        return self.base_path / key

    async def upload(self, key: str, data: bytes, content_type: str = "") -> str:
        """Upload a file to local filesystem."""
        full_path = self._full_path(key)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(str(full_path), "wb") as f:
            await f.write(data)
        return key

    async def get(self, key: str) -> Optional[bytes]:
        """Get file contents from local filesystem."""
        full_path = self._full_path(key)
        if not full_path.exists():
            return None
        async with aiofiles.open(str(full_path), "rb") as f:
            return await f.read()

    async def delete(self, key: str) -> bool:
        """Delete a file from local filesystem."""
        full_path = self._full_path(key)
        if full_path.exists():
            os.remove(str(full_path))
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if file exists on local filesystem."""
        return self._full_path(key).exists()

    def get_url(self, key: str) -> str:
        """Get the URL path for serving a file."""
        if key.startswith("http://") or key.startswith("https://"):
            return key
        return f"/storage/{key}"


def generate_storage_key(prefix: str, extension: str) -> str:
    """Generate a unique storage key for a file."""
    unique_id = uuid.uuid4().hex[:12]
    return f"{prefix}/{unique_id}.{extension}"


def get_storage(storage_type: str = "local", storage_path: str = "/app/storage") -> StorageBackend:
    """Factory function to create a storage backend."""
    if storage_type == "local":
        return LocalStorage(storage_path)
    # Future: elif storage_type == "r2": return R2Storage(...)
    raise ValueError(f"Unknown storage type: {storage_type}")
