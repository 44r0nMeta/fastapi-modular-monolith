from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.core.dependencies import DBSession, Pagination
from app.core.pagination import Page
from app.modules.auth import CurrentUser
from app.modules.items.schemas import ItemCreate, ItemDetail, ItemRead, ItemUpdate
from app.modules.items.service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate, user: CurrentUser, session: DBSession
) -> ItemRead:
    item = await ItemService(session).create(user.id, data)
    return ItemRead.model_validate(item)


@router.get("", response_model=Page[ItemRead])
async def list_items(
    user: CurrentUser, session: DBSession, params: Pagination
) -> Page[ItemRead]:
    page = await ItemService(session).list(user.id, params)
    return Page[ItemRead].create(
        [ItemRead.model_validate(i) for i in page.items], page.total, params
    )


@router.get("/{item_id}", response_model=ItemDetail)
async def get_item(
    item_id: uuid.UUID, user: CurrentUser, session: DBSession
) -> ItemDetail:
    item, owner = await ItemService(session).get_with_owner(user.id, item_id)
    return ItemDetail.model_validate(item).model_copy(update={"owner": owner})


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: uuid.UUID, data: ItemUpdate, user: CurrentUser, session: DBSession
) -> ItemRead:
    item = await ItemService(session).update(user.id, item_id, data)
    return ItemRead.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID, user: CurrentUser, session: DBSession
) -> None:
    await ItemService(session).delete(user.id, item_id)
