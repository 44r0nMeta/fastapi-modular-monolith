from __future__ import annotations

from app.core.repository import BaseRepository
from app.modules.items.models import Item


class ItemRepository(BaseRepository[Item]):
    model = Item
