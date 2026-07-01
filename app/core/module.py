"""Module abstraction + auto-discovery.

A *module* is a self-contained feature slice (its own models, schemas,
repository, service, routes, events). Each module package exposes a single
`module = Module(...)` in its `__init__.py`. At startup the app scans
`app/modules/*`, imports each package (which imports its models & listeners as a
side effect), and registers every module's router automatically.

This is the "easier" win over hand-wiring every router: drop in a new module
folder (or run `python -m app.cli new-module <name>`) and it self-registers.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger("app.modules")

Hook = Callable[[], Awaitable[None]]


@dataclass
class Module:
    name: str
    router: APIRouter | None = None
    order: int = 100  # lower = registered/started earlier
    on_startup: Hook | None = None
    on_shutdown: Hook | None = None
    tags: list[str] = field(default_factory=list)


def discover_modules(package: str = "app.modules") -> list[Module]:
    """Import every sub-package of `package` and collect their `module` objects."""
    pkg = importlib.import_module(package)
    found: list[Module] = []
    for info in pkgutil.iter_modules(pkg.__path__):
        if not info.ispkg:
            continue
        mod = importlib.import_module(f"{package}.{info.name}")
        candidate = getattr(mod, "module", None)
        if isinstance(candidate, Module):
            found.append(candidate)
        else:
            logger.warning("module_without_definition", package=info.name)
    found.sort(key=lambda m: (m.order, m.name))
    logger.info("modules_discovered", modules=[m.name for m in found])
    return found
