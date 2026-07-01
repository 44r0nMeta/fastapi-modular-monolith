"""Auth-owned event listeners.

Auth currently reacts to nothing itself — cross-module reactions live in the
consuming module (see `app/modules/items/listeners.py` reacting to
`UserRegistered`). Kept as the conventional home for any future auth listeners.
"""

from __future__ import annotations
