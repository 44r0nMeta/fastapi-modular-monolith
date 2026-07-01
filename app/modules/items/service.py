from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import Page, PageParams
from app.modules.auth import AuthGateway, PublicUser
from app.modules.items.models import Item
from app.modules.items.repository import ItemRepository
from app.modules.items.schemas import ItemCreate, ItemUpdate


class ItemService:
    """All queries are scoped to `owner_id`. A resource owned by someone else is
    reported as 404 (anti-IDOR) — never 403, which would leak its existence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.items = ItemRepository(session)
        self.auth = AuthGateway(session)

    async def create(self, owner_id: uuid.UUID, data: ItemCreate) -> Item:
        item = await self.items.create(
            Item(owner_id=owner_id, title=data.title, description=data.description)
        )
        await self.session.commit()
        return item

    async def get(self, owner_id: uuid.UUID, item_id: uuid.UUID) -> Item:
        return await self.items.get_or_404(item_id, owner_id=owner_id)

    async def get_with_owner(
        self, owner_id: uuid.UUID, item_id: uuid.UUID
    ) -> tuple[Item, PublicUser | None]:
        item = await self.get(owner_id, item_id)
        owner = await self.auth.get_user(item.owner_id)
        return item, owner

    async def list(self, owner_id: uuid.UUID, params: PageParams) -> Page[Item]:
        return await self.items.paginate(
            params,
            filters={"owner_id": owner_id},
            order_by=Item.created_at.desc(),
        )

    async def update(
        self, owner_id: uuid.UUID, item_id: uuid.UUID, data: ItemUpdate
    ) -> Item:
        item = await self.get(owner_id, item_id)
        item = await self.items.update(item, data.model_dump(exclude_unset=True))
        await self.session.commit()
        return item

    async def delete(self, owner_id: uuid.UUID, item_id: uuid.UUID) -> None:
        item = await self.get(owner_id, item_id)
        await self.items.delete(item)
        await self.session.commit()

    async def create_welcome(self, owner_id: uuid.UUID) -> Item:
        item = await self.items.create(
            Item(
                owner_id=owner_id,
                title="Welcome 👋",
                description="This starter item was created by an event listener "
                "reacting to your registration.",
            )
        )
        await self.session.commit()
        return item
