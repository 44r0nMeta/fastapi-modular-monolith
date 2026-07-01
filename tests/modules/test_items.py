from __future__ import annotations

from httpx import AsyncClient

ITEMS = "/api/v1/items"


async def test_welcome_item_created_by_event(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    # Registering the fixture user emitted UserRegistered, which the items
    # module's listener reacted to by creating a welcome item.
    r = await client.get(ITEMS, headers=auth_headers)
    assert r.status_code == 200
    titles = [i["title"] for i in r.json()["items"]]
    assert any("Welcome" in t for t in titles)


async def test_item_crud(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    r = await client.post(
        ITEMS, headers=auth_headers, json={"title": "Buy milk", "description": "2L"}
    )
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = await client.patch(
        f"{ITEMS}/{item_id}", headers=auth_headers, json={"is_done": True}
    )
    assert r.status_code == 200
    assert r.json()["is_done"] is True

    r = await client.get(f"{ITEMS}/{item_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["owner"]["email"] == "user@example.com"  # gateway enrichment

    r = await client.delete(f"{ITEMS}/{item_id}", headers=auth_headers)
    assert r.status_code == 204

    r = await client.get(f"{ITEMS}/{item_id}", headers=auth_headers)
    assert r.status_code == 404  # soft-deleted -> gone


async def test_anti_idor_returns_404(client: AsyncClient) -> None:
    # User one creates an item.
    await client.post(
        "/api/v1/auth/register",
        json={"email": "one@x.com", "password": "supersecret"},
    )
    t1 = (
        await client.post(
            "/api/v1/auth/login",
            json={"email": "one@x.com", "password": "supersecret"},
        )
    ).json()["access_token"]
    item_id = (
        await client.post(
            ITEMS, headers={"Authorization": f"Bearer {t1}"}, json={"title": "secret"}
        )
    ).json()["id"]

    # User two must not see it — 404, never 403 (no existence leak).
    await client.post(
        "/api/v1/auth/register",
        json={"email": "two@x.com", "password": "supersecret"},
    )
    t2 = (
        await client.post(
            "/api/v1/auth/login",
            json={"email": "two@x.com", "password": "supersecret"},
        )
    ).json()["access_token"]
    r = await client.get(
        f"{ITEMS}/{item_id}", headers={"Authorization": f"Bearer {t2}"}
    )
    assert r.status_code == 404
