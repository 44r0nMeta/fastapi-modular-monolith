"""Cross-module async reaction: when auth emits `UserRegistered`, items seeds a
welcome item. Demonstrates decoupled inter-module comms via the event bus —
items depends on auth's *event*, never on auth internals."""

from __future__ import annotations

from app.core.database import AsyncSessionLocal
from app.core.events import on
from app.core.logging import get_logger
from app.modules.auth import UserRegistered
from app.modules.items.service import ItemService

logger = get_logger("items.listeners")


@on(UserRegistered)
async def create_welcome_item(event: UserRegistered) -> None:
    async with AsyncSessionLocal() as session:
        await ItemService(session).create_welcome(event.user_id)
    logger.info("welcome_item_created", user_id=str(event.user_id))
