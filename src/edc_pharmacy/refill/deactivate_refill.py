def deactivate_refill(rx_refill):
    """Deactivates this refill."""
    if rx_refill.active:
        rx_refill.active = False
        rx_refill.save()
        rx_refill.refresh_from_db()
