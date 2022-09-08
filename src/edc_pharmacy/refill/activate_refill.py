from __future__ import annotations

from .deactivate_refill import deactivate_refill
from .get_active_refill import get_active_refill


def activate_refill(rx_refill):
    """Activates this rx_refill and deactivates the active rx_refill,
    if there is one.
    """
    if active_rx_refill := get_active_refill(rx_refill.rx):
        if active_rx_refill != rx_refill:
            deactivate_refill(active_rx_refill)
    rx_refill.active = True
    rx_refill.save()
    rx_refill.refresh_from_db()
