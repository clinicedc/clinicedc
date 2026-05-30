from __future__ import annotations

import threading
from contextlib import contextmanager

_tl = threading.local()


@contextmanager
def apply_delta_context():
    _tl.active = True
    try:
        yield
    finally:
        _tl.active = False


def is_apply_delta_active() -> bool:
    return getattr(_tl, "active", False)
