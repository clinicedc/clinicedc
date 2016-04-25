
def displayed_choice(choices, stored_choice):
    """Returns the display choice of the choice tuple given the stored choice."""
    displayed_choice = None
    STORED_CHOICE = 0
    DISPLAYED_CHOICE = 1
    for choice in choices:
        if choice[STORED_CHOICE] == stored_choice:
            displayed_choice = choice[DISPLAYED_CHOICE]
    if not displayed_choice:
        raise ValueError(
            '\'{}\' is not a stored value in choices tuple. Got {}.'.format(stored_choice, choices))
    return displayed_choice
