from __future__ import annotations

import uuid

from sqlmodel import Field

from app.core.models import BaseModel, SoftDeleteMixin


class Item(BaseModel, SoftDeleteMixin, table=True):
    __tablename__ = "items"

    owner_id: uuid.UUID = Field(index=True, foreign_key="users.id", nullable=False)
    title: str = Field(nullable=False)
    description: str | None = Field(default=None)
    is_done: bool = Field(default=False, nullable=False)
