from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import Field

from app.core.schemas import BaseSchema
from app.modules.auth import PublicUser


class ItemCreate(BaseSchema):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class ItemUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    is_done: bool | None = None


class ItemRead(BaseSchema):
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: str | None
    is_done: bool
    created_at: datetime
    updated_at: datetime


class ItemDetail(ItemRead):
    """Detail view enriched with owner info fetched via the auth gateway."""

    owner: PublicUser | None = None
