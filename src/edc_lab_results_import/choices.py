from .constants import ERROR, IMPORTED, PENDING

STATUS_CHOICES = [
    (PENDING, "Pending"),
    (IMPORTED, "Imported"),
    (ERROR, "Error"),
]
