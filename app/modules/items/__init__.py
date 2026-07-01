"""Items module — an example owner-scoped CRUD feature slice.

Copy this module (or run `python -m app.cli new-module <name>`) as the template
for your own features.
"""

from __future__ import annotations

from app.core.module import Module

# Import side effects: register model (Alembic) + event listeners.
from app.modules.items import listeners as listeners  # noqa: F401
from app.modules.items import models as models  # noqa: F401
from app.modules.items.routes.v1 import item_routes

module = Module(
    name="items",
    router=item_routes.router,
    order=20,
    tags=["items"],
)

__all__ = ["module"]
