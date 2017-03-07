
def get_display(choices, label):
    """Returns the display value of a choices tuple for label."""
    for choice in choices:
        store_value, display_value = choice
        if label == store_value:
            return display_value
    return None
